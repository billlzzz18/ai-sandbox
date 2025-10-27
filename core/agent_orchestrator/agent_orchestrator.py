# core/agent_orchestrator/agent_orchestrator.py

import asyncio
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

from ..message_bus.message_bus import MessageBus, get_message_bus
from ..agent_communication.agent_communication import AgentCommunicator, CollaborationContext
from ..workflow_engine.workflow_engine import WorkflowEngine
from ...memory.episodic_memory.episodic_memory import EpisodicMemory, Experience
from ...memory.semantic_memory.knowledge_graph import KnowledgeGraph
from ...memory.working_memory.working_memory import WorkingMemory, MemoryItem, MemoryItemPriority


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    name: str
    role: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    last_seen: float = field(default_factory=time.time)
    communicator: Optional[AgentCommunicator] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """Central orchestrator for multi-agent systems"""

    def __init__(self):
        self.message_bus = get_message_bus()
        self.workflow_engine = WorkflowEngine(orchestrator=self)

        # Agent registry
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_lock = threading.Lock()

        # Memory systems
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = KnowledgeGraph()
        self.working_memory = WorkingMemory(max_items=50)

        # Active collaborations
        self.collaborations: Dict[str, CollaborationContext] = {}
        self.collaboration_lock = threading.Lock()

        # Statistics
        self.stats = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'active_collaborations': 0,
            'total_collaborations': 0
        }

    def register_agent(self, agent_name: str, role: str, capabilities: List[str],
                      metadata: Dict[str, Any] = None) -> AgentCommunicator:
        """Register a new agent with the orchestrator"""

        with self.agent_lock:
            if agent_name in self.agents:
                raise ValueError(f"Agent '{agent_name}' already registered")

            communicator = AgentCommunicator(agent_name)

            # Register task and collaboration handlers
            communicator.register_task_handler(self._handle_task_request)
            communicator.register_collaboration_handler(self._handle_collaboration_offer)

            agent_info = AgentInfo(
                name=agent_name,
                role=role,
                capabilities=capabilities,
                status=AgentStatus.IDLE,
                communicator=communicator,
                metadata=metadata or {}
            )

            self.agents[agent_name] = agent_info

            # Add to semantic memory
            self.semantic_memory.add_triple(agent_name, "is_a", role, source="orchestrator")
            for capability in capabilities:
                self.semantic_memory.add_triple(agent_name, "can_do", capability, source="orchestrator")

            return communicator

    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""

        with self.agent_lock:
            if agent_name not in self.agents:
                return

            agent_info = self.agents[agent_name]

            # Clean up communicator
            if agent_info.communicator:
                agent_info.communicator.cleanup()

            del self.agents[agent_name]

    def execute_task(self, agent_name: str, task: Dict[str, Any]) -> Any:
        """Execute a task on a specific agent"""

        with self.agent_lock:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not registered")

            agent_info = self.agents[agent_name]
            if agent_info.status != AgentStatus.IDLE:
                raise RuntimeError(f"Agent '{agent_name}' is not available")

        # Mark agent as busy
        agent_info.status = AgentStatus.BUSY
        start_time = time.time()

        try:
            # Send task request
            result = agent_info.communicator.send_task_request(
                target_agent=agent_name,
                task=task
            )

            # Mark as successful
            agent_info.status = AgentStatus.IDLE
            self.stats['total_tasks'] += 1
            self.stats['successful_tasks'] += 1

            # Store experience
            execution_time = time.time() - start_time
            experience = Experience(
                task=f"{task.get('action', 'unknown')} on {agent_name}",
                success=True,
                context={'agent': agent_name, 'task': task},
                lessons_learned=[],
                performance_metrics={'execution_time': execution_time},
                agent_name=agent_name,
                task_type=task.get('action', 'unknown')
            )
            self.episodic_memory.store_experience(experience)

            # Add to working memory
            self.working_memory.add_item(
                data={'task': task, 'result': result, 'agent': agent_name},
                priority=MemoryItemPriority.MEDIUM,
                tags=['task', 'success', agent_name]
            )

            return result

        except Exception as e:
            # Mark as error
            agent_info.status = AgentStatus.ERROR
            self.stats['total_tasks'] += 1
            self.stats['failed_tasks'] += 1

            # Store failed experience
            execution_time = time.time() - start_time
            experience = Experience(
                task=f"{task.get('action', 'unknown')} on {agent_name}",
                success=False,
                context={'agent': agent_name, 'task': task, 'error': str(e)},
                lessons_learned=[f"Task failed: {str(e)}"],
                performance_metrics={'execution_time': execution_time},
                agent_name=agent_name,
                task_type=task.get('action', 'unknown')
            )
            self.episodic_memory.store_experience(experience)

            # Add to working memory
            self.working_memory.add_item(
                data={'task': task, 'error': str(e), 'agent': agent_name},
                priority=MemoryItemPriority.HIGH,
                tags=['task', 'error', agent_name]
            )

            raise

    def start_collaboration(self, initiator: str, participants: List[str],
                          collaboration_type: str, context: Dict[str, Any]) -> str:
        """Start a new collaboration"""

        collaboration_id = f"collab_{int(time.time() * 1000)}"

        collaboration = CollaborationContext(
            collaboration_id=collaboration_id,
            initiator=initiator,
            participants=[initiator] + participants,
            collaboration_type=collaboration_type,
            shared_context=context
        )

        with self.collaboration_lock:
            self.collaborations[collaboration_id] = collaboration
            self.stats['active_collaborations'] += 1
            self.stats['total_collaborations'] += 1

        # Notify participants
        for participant in participants:
            if participant in self.agents:
                self.agents[participant].communicator.offer_collaboration(
                    target_agent=participant,
                    collaboration_type=collaboration_type,
                    context=context
                )

        return collaboration_id

    def execute_workflow(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow using the workflow engine"""
        return self.workflow_engine.execute_workflow(workflow_name, input_data)

    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""

        with self.agent_lock:
            if agent_name not in self.agents:
                return None

            agent_info = self.agents[agent_name]
            return {
                'name': agent_info.name,
                'role': agent_info.role,
                'capabilities': agent_info.capabilities,
                'status': agent_info.status.value,
                'last_seen': agent_info.last_seen,
                'metadata': agent_info.metadata
            }

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get information about all registered agents"""

        with self.agent_lock:
            return [
                {
                    'name': agent.name,
                    'role': agent.role,
                    'capabilities': agent.capabilities,
                    'status': agent.status.value,
                    'last_seen': agent.last_seen
                }
                for agent in self.agents.values()
            ]

    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability"""

        with self.agent_lock:
            return [
                agent_name for agent_name, agent_info in self.agents.items()
                if capability in agent_info.capabilities and agent_info.status == AgentStatus.IDLE
            ]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""

        return {
            'episodic': self.episodic_memory.get_performance_stats('orchestrator'),
            'semantic': self.semantic_memory.get_statistics(),
            'working': self.working_memory.get_statistics()
        }

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""

        with self.collaboration_lock:
            active_collab_count = len([
                c for c in self.collaborations.values()
                if c.status == 'active'
            ])

        return {
            **self.stats,
            'registered_agents': len(self.agents),
            'active_collaborations': active_collab_count,
            'idle_agents': len([a for a in self.agents.values() if a.status == AgentStatus.IDLE]),
            'busy_agents': len([a for a in self.agents.values() if a.status == AgentStatus.BUSY])
        }

    def _handle_task_request(self, message) -> Dict[str, Any]:
        """Handle task requests from agents"""
        # This would be called when one agent requests work from another
        # For now, return a simple acknowledgment
        return {
            'status': 'received',
            'message': f"Task request from {message.sender} processed",
            'timestamp': time.time()
        }

    def _handle_collaboration_offer(self, message) -> Dict[str, Any]:
        """Handle collaboration offers"""
        collaboration_type = message.payload.get('collaboration_type', 'unknown')

        # Simple acceptance logic - in production this would be more sophisticated
        if collaboration_type in ['code_review', 'planning', 'analysis']:
            return {
                'accepted': True,
                'reason': f"Accepting {collaboration_type} collaboration",
                'capabilities': self.agents[message.receiver].capabilities
            }
        else:
            return {
                'accepted': False,
                'reason': f"Not suitable for {collaboration_type} collaboration"
            }

    def cleanup(self):
        """Clean up resources"""

        # Clean up agents
        with self.agent_lock:
            for agent_info in self.agents.values():
                if agent_info.communicator:
                    agent_info.communicator.cleanup()
            self.agents.clear()

        # Clean up collaborations
        with self.collaboration_lock:
            self.collaborations.clear()

        # Clean up workflow engine
        self.workflow_engine.cleanup()


# Global orchestrator instance
_global_orchestrator = None

def get_orchestrator() -> AgentOrchestrator:
    """Get the global orchestrator instance"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = AgentOrchestrator()
    return _global_orchestrator

def reset_orchestrator():
    """Reset the global orchestrator (for testing)"""
    global _global_orchestrator
    if _global_orchestrator:
        _global_orchestrator.cleanup()
    _global_orchestrator = None