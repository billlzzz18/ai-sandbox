# core/message_bus/message_bus.py

import asyncio
import json
import time
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
import threading
import queue


class Message:
    """Message container for agent communication"""

    def __init__(self, message_type: str, sender: str, receiver: Optional[str] = None,
                 payload: Any = None, correlation_id: Optional[str] = None, priority: int = 1):
        self.message_type = message_type  # 'request', 'response', 'notification', 'broadcast'
        self.sender = sender
        self.receiver = receiver  # None for broadcasts
        self.payload = payload or {}
        self.correlation_id = correlation_id or self._generate_id()
        self.priority = priority  # 1=low, 5=high
        self.timestamp = time.time()
        self.ttl = 300  # Time to live in seconds

    def _generate_id(self) -> str:
        return f"{self.sender}_{int(self.timestamp * 1000)}"

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_type': self.message_type,
            'sender': self.sender,
            'receiver': self.receiver,
            'payload': self.payload,
            'correlation_id': self.correlation_id,
            'priority': self.priority,
            'timestamp': self.timestamp,
            'ttl': self.ttl
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        msg = cls(
            message_type=data['message_type'],
            sender=data['sender'],
            receiver=data.get('receiver'),
            payload=data.get('payload', {}),
            correlation_id=data.get('correlation_id'),
            priority=data.get('priority', 1)
        )
        msg.timestamp = data.get('timestamp', time.time())
        msg.ttl = data.get('ttl', 300)
        return msg


class MessageBus:
    """Central message bus for agent communication"""

    def __init__(self):
        self.subscribers = defaultdict(list)  # topic -> [callbacks]
        self.message_queue = queue.PriorityQueue()  # (priority, message)
        self.response_futures = {}  # correlation_id -> Future
        self.running = False
        self.worker_thread = None

        # Message statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_expired': 0,
            'subscribers_count': 0
        }

    def start(self):
        """Start the message bus processing"""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.worker_thread.start()

    def stop(self):
        """Stop the message bus processing"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def subscribe(self, topic: str, callback: Callable[[Message], None]) -> str:
        """Subscribe to a topic"""
        subscription_id = f"{topic}_{id(callback)}"
        self.subscribers[topic].append((subscription_id, callback))
        self.stats['subscribers_count'] = sum(len(callbacks) for callbacks in self.subscribers.values())
        return subscription_id

    def unsubscribe(self, subscription_id: str):
        """Unsubscribe from a topic"""
        for topic, callbacks in self.subscribers.items():
            self.subscribers[topic] = [(sid, cb) for sid, cb in callbacks if sid != subscription_id]
        self.stats['subscribers_count'] = sum(len(callbacks) for callbacks in self.subscribers.values())

    def publish(self, message: Message):
        """Publish a message to the bus"""
        if message.is_expired():
            self.stats['messages_expired'] += 1
            return

        # Add to priority queue (negative priority for higher priority first)
        self.message_queue.put((-message.priority, message))
        self.stats['messages_sent'] += 1

    def send_request(self, message: Message, timeout: float = 30.0) -> Optional[Any]:
        """Send a request and wait for response"""
        if not isinstance(message, Message) or message.message_type != 'request':
            raise ValueError("Message must be a request type")

        # Create a future for the response
        future = asyncio.Future()
        self.response_futures[message.correlation_id] = future

        # Publish the request
        self.publish(message)

        # Wait for response (simplified - in real async system this would be better)
        try:
            # This is a blocking wait - in production you'd want async handling
            import concurrent.futures
            return concurrent.futures.wait([future], timeout=timeout)[0][0].result()
        except Exception as e:
            # Clean up future
            self.response_futures.pop(message.correlation_id, None)
            raise e

    def _process_messages(self):
        """Process messages from the queue"""
        while self.running:
            try:
                # Get message with timeout to allow checking running flag
                priority, message = self.message_queue.get(timeout=1.0)

                if message.is_expired():
                    self.stats['messages_expired'] += 1
                    continue

                self.stats['messages_received'] += 1

                # Route message based on type
                if message.message_type == 'broadcast':
                    self._handle_broadcast(message)
                elif message.message_type == 'response':
                    self._handle_response(message)
                else:
                    self._handle_direct_message(message)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")

    def _handle_broadcast(self, message: Message):
        """Handle broadcast messages"""
        topic = f"broadcast.{message.message_type}"
        for subscription_id, callback in self.subscribers[topic]:
            try:
                callback(message)
            except Exception as e:
                print(f"Error in broadcast callback {subscription_id}: {e}")

    def _handle_response(self, message: Message):
        """Handle response messages"""
        correlation_id = message.correlation_id
        if correlation_id in self.response_futures:
            future = self.response_futures.pop(correlation_id)
            if not future.done():
                future.set_result(message.payload)

    def _handle_direct_message(self, message: Message):
        """Handle direct messages to specific receivers"""
        if message.receiver:
            topic = f"agent.{message.receiver}"
            for subscription_id, callback in self.subscribers[topic]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error in direct message callback {subscription_id}: {e}")
        else:
            # No receiver specified, treat as broadcast
            self._handle_broadcast(message)

    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return self.stats.copy()

    def clear_expired_messages(self):
        """Clear expired messages from futures"""
        current_time = time.time()
        expired_ids = [
            cid for cid, future in self.response_futures.items()
            if current_time - future._creation_time > 300  # 5 minutes timeout
        ]
        for cid in expired_ids:
            self.response_futures.pop(cid, None)


# Global message bus instance
_global_bus = None

def get_message_bus() -> MessageBus:
    """Get the global message bus instance"""
    global _global_bus
    if _global_bus is None:
        _global_bus = MessageBus()
        _global_bus.start()
    return _global_bus

def reset_message_bus():
    """Reset the global message bus (for testing)"""
    global _global_bus
    if _global_bus:
        _global_bus.stop()
    _global_bus = None