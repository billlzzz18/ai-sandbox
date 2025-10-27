# core/agent_communication/agent_communication.py

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading

from ..message_bus.message_bus import Message, MessageBus, get_message_bus


@dataclass
class AgentMessage:
    """Structured message for agent communication"""
    sender: str
    receiver: str
    message_type: str  # 'task_request', 'task_response', 'status_update', 'collaboration_offer'
    payload: Dict[str, Any]
    correlation_id: str
    priority: int = 1
    requires_response: bool = False
    collaboration_context: Optional[Dict[str, Any]] = None

    def to_message(self) -> Message:
        """Convert to MessageBus Message"""
        return Message(
            message_type=self.message_type,
            sender=self.sender,
            receiver=self.receiver,
            payload={
                'data': self.payload,
                'collaboration_context': self.collaboration_context,
                'requires_response': self.requires_response
            },
            correlation_id=self.correlation_id,
            priority=self.priority
        )

    @classmethod
    def from_message(cls, message: Message) -> 'AgentMessage':
        """Create from MessageBus Message"""
        payload = message.payload
        return cls(
            sender=message.sender,
            receiver=message.receiver or '',
            message_type=message.message_type,
            payload=payload.get('data', {}),
            correlation_id=message.correlation_id,
            priority=message.priority,
            requires_response=payload.get('requires_response', False),
            collaboration_context=payload.get('collaboration_context')
        )


class AgentCommunicator:
    """Handles agent-to-agent communication"""

    def __init__(self, agent_name: str, message_bus: Optional[MessageBus] = None):
        self.agent_name = agent_name
        self.message_bus = message_bus or get_message_bus()
        self.response_handlers = {}  # correlation_id -> handler
        self.collaboration_handlers = {}  # message_type -> handler
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Subscribe to messages for this agent
        self.message_bus.subscribe(f"agent.{agent_name}", self._handle_message)

    def send_task_request(self, target_agent: str, task: Dict[str, Any],
                         priority: int = 1, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send a task request to another agent and wait for response"""

        correlation_id = f"{self.agent_name}_task_{int(time.time() * 1000)}"

        message = AgentMessage(
            sender=self.agent_name,
            receiver=target_agent,
            message_type='task_request',
            payload={'task': task},
            correlation_id=correlation_id,
            priority=priority,
            requires_response=True
        )

        # Create future for response
        future = asyncio.Future()

        def response_handler(response_payload):
            if not future.done():
                future.set_result(response_payload)

        self.response_handlers[correlation_id] = response_handler

        # Send message
        self.message_bus.publish(message.to_message())

        # Wait for response
        try:
            return asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            # Clean up handler
            self.response_handlers.pop(correlation_id, None)
            raise TimeoutError(f"Task request to {target_agent} timed out")
        finally:
            # Clean up
            self.response_handlers.pop(correlation_id, None)

    def send_task_response(self, original_message: AgentMessage, response: Dict[str, Any]):
        """Send a response to a task request"""

        response_message = AgentMessage(
            sender=self.agent_name,
            receiver=original_message.sender,
            message_type='task_response',
            payload={'response': response, 'original_task': original_message.payload},
            correlation_id=original_message.correlation_id,
            priority=original_message.priority,
            requires_response=False
        )

        self.message_bus.publish(response_message.to_message())

    def broadcast_status_update(self, status: Dict[str, Any]):
        """Broadcast status update to all agents"""

        message = AgentMessage(
            sender=self.agent_name,
            receiver='',  # Broadcast
            message_type='status_update',
            payload={'status': status},
            correlation_id=f"{self.agent_name}_status_{int(time.time() * 1000)}",
            priority=1,
            requires_response=False
        )

        self.message_bus.publish(message.to_message())

    def offer_collaboration(self, target_agent: str, collaboration_type: str,
                          context: Dict[str, Any], priority: int = 2) -> Optional[Dict[str, Any]]:
        """Offer collaboration to another agent"""

        correlation_id = f"{self.agent_name}_collab_{int(time.time() * 1000)}"

        message = AgentMessage(
            sender=self.agent_name,
            receiver=target_agent,
            message_type='collaboration_offer',
            payload={
                'collaboration_type': collaboration_type,
                'context': context
            },
            correlation_id=correlation_id,
            priority=priority,
            requires_response=True,
            collaboration_context=context
        )

        # Create future for response
        future = asyncio.Future()

        def response_handler(response_payload):
            if not future.done():
                future.set_result(response_payload)

        self.response_handlers[correlation_id] = response_handler

        # Send message
        self.message_bus.publish(message.to_message())

        # Wait for response
        try:
            return asyncio.wait_for(future, timeout=60.0)  # Longer timeout for collaboration
        except asyncio.TimeoutError:
            self.response_handlers.pop(correlation_id, None)
            return {'accepted': False, 'reason': 'timeout'}
        finally:
            self.response_handlers.pop(correlation_id, None)

    def register_task_handler(self, handler: Callable[[AgentMessage], Dict[str, Any]]):
        """Register handler for task requests"""
        self.collaboration_handlers['task_request'] = handler

    def register_collaboration_handler(self, handler: Callable[[AgentMessage], Dict[str, Any]]):
        """Register handler for collaboration offers"""
        self.collaboration_handlers['collaboration_offer'] = handler

    def _handle_message(self, message: Message):
        """Handle incoming messages"""
        try:
            agent_message = AgentMessage.from_message(message)

            # Handle responses
            if agent_message.message_type == 'task_response':
                handler = self.response_handlers.get(agent_message.correlation_id)
                if handler:
                    handler(agent_message.payload.get('response', {}))
                return

            # Handle collaboration responses
            if agent_message.message_type.endswith('_response') and agent_message.correlation_id in self.response_handlers:
                handler = self.response_handlers[agent_message.correlation_id]
                if handler:
                    handler(agent_message.payload)
                return

            # Handle requests and offers
            handler = self.collaboration_handlers.get(agent_message.message_type)
            if handler:
                # Process in thread pool to avoid blocking
                self.executor.submit(self._process_request, agent_message, handler)
            else:
                print(f"No handler for message type: {agent_message.message_type}")

        except Exception as e:
            print(f"Error handling message: {e}")

    def _process_request(self, message: AgentMessage, handler: Callable):
        """Process a request in a separate thread"""
        try:
            response = handler(message)

            if message.requires_response:
                if message.message_type == 'task_request':
                    self.send_task_response(message, response)
                elif message.message_type == 'collaboration_offer':
                    # Send collaboration response
                    response_message = AgentMessage(
                        sender=self.agent_name,
                        receiver=message.sender,
                        message_type='collaboration_response',
                        payload=response,
                        correlation_id=message.correlation_id,
                        priority=message.priority,
                        requires_response=False
                    )
                    self.message_bus.publish(response_message.to_message())

        except Exception as e:
            print(f"Error processing request: {e}")

            # Send error response if required
            if message.requires_response:
                error_response = {'error': str(e), 'success': False}
                if message.message_type == 'task_request':
                    self.send_task_response(message, error_response)

    def cleanup(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)


class CollaborationContext:
    """Context for multi-agent collaboration"""

    def __init__(self, collaboration_id: str, initiator: str, participants: List[str],
                 collaboration_type: str, shared_context: Dict[str, Any]):
        self.collaboration_id = collaboration_id
        self.initiator = initiator
        self.participants = participants
        self.collaboration_type = collaboration_type
        self.shared_context = shared_context
        self.start_time = time.time()
        self.status = 'active'  # 'active', 'completed', 'failed'
        self.results = {}

    def add_participant(self, agent_name: str):
        """Add a participant to the collaboration"""
        if agent_name not in self.participants:
            self.participants.append(agent_name)

    def update_result(self, agent_name: str, result: Any):
        """Update result from a participant"""
        self.results[agent_name] = {
            'result': result,
            'timestamp': time.time()
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get collaboration summary"""
        return {
            'collaboration_id': self.collaboration_id,
            'initiator': self.initiator,
            'participants': self.participants,
            'collaboration_type': self.collaboration_type,
            'status': self.status,
            'duration': time.time() - self.start_time,
            'results_count': len(self.results),
            'shared_context': self.shared_context
        }

    def complete(self):
        """Mark collaboration as completed"""
        self.status = 'completed'

    def fail(self, reason: str):
        """Mark collaboration as failed"""
        self.status = 'failed'
        self.shared_context['failure_reason'] = reason