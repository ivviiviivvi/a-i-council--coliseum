"""
Notification System Module

Handles event notifications to users and systems.
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from .processing import ProcessedEvent


class NotificationChannel(str, Enum):
    """Notification channels"""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Notification message"""
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    channel: NotificationChannel
    priority: NotificationPriority
    recipient: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    sent: bool = False
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationSystem:
    """
    System for sending notifications about events
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, Dict[str, List[NotificationChannel]]] = {}
        self.notification_queue: List[Notification] = []
        self.sent_notifications: List[Notification] = []
        self.handlers: Dict[NotificationChannel, Callable] = {}
    
    def subscribe(
        self,
        user_id: str,
        topic: str,
        channels: List[NotificationChannel]
    ) -> None:
        """
        Subscribe user to topic notifications
        
        Args:
            user_id: User identifier
            topic: Topic to subscribe to
            channels: Channels for notifications
        """
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = {}
        self.subscriptions[user_id][topic] = channels
    
    def unsubscribe(self, user_id: str, topic: str) -> None:
        """Unsubscribe user from topic"""
        if user_id in self.subscriptions:
            if topic in self.subscriptions[user_id]:
                del self.subscriptions[user_id][topic]
    
    def register_handler(
        self,
        channel: NotificationChannel,
        handler: Callable
    ) -> None:
        """Register a handler for a notification channel"""
        self.handlers[channel] = handler
    
    async def notify_event(
        self,
        event: ProcessedEvent,
        topic: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM
    ) -> List[Notification]:
        """
        Create notifications for an event
        
        Args:
            event: Event to notify about
            topic: Optional topic filter
            priority: Notification priority
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        # Determine topic from event
        if not topic:
            topic = event.category or "general"
        
        # Find subscribers
        for user_id, topics in self.subscriptions.items():
            if topic in topics:
                channels = topics[topic]
                for channel in channels:
                    notification = Notification(
                        event_id=event.event_id,
                        channel=channel,
                        priority=priority,
                        recipient=user_id,
                        title=event.title,
                        message=event.summary or event.description[:100],
                        data={"event": event.model_dump()}
                    )
                    notifications.append(notification)
                    self.notification_queue.append(notification)
        
        return notifications
    
    async def send_notification(self, notification: Notification) -> bool:
        """
        Send a notification through its channel
        
        Args:
            notification: Notification to send
            
        Returns:
            True if sent successfully
        """
        handler = self.handlers.get(notification.channel)
        if not handler:
            print(f"No handler for channel: {notification.channel}")
            return False
        
        try:
            await handler(notification)
            notification.sent = True
            notification.sent_at = datetime.utcnow()
            self.sent_notifications.append(notification)
            return True
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    async def process_queue(self) -> int:
        """
        Process notification queue
        
        Returns:
            Number of notifications sent
        """
        sent_count = 0
        remaining = []
        
        for notification in self.notification_queue:
            if await self.send_notification(notification):
                sent_count += 1
            else:
                remaining.append(notification)
        
        self.notification_queue = remaining
        return sent_count
    
    def get_user_subscriptions(self, user_id: str) -> Dict[str, List[str]]:
        """Get all subscriptions for a user"""
        if user_id not in self.subscriptions:
            return {}
        
        return {
            topic: [c.value for c in channels]
            for topic, channels in self.subscriptions[user_id].items()
        }
    
    def get_notification_stats(self) -> Dict[str, int]:
        """Get notification statistics"""
        return {
            "queued": len(self.notification_queue),
            "sent": len(self.sent_notifications),
            "subscribers": len(self.subscriptions)
        }
