"""Notification-related events for Fleet Tracker"""
from typing import Optional, Dict, Any, List
from .base_event import BaseEvent

class AlertCreatedEvent(BaseEvent):
    """Event emitted when an alert is created"""
    
    def __init__(self, alert_id: str, vehicle_id: str, alert_type: str, severity: str, message: str, **kwargs):
        super().__init__(
            event_type="alert.created",
            source_service="notification-service",
            data={
                "alert_id": alert_id,
                "vehicle_id": vehicle_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message
            },
            **kwargs
        )

class AlertResolvedEvent(BaseEvent):
    """Event emitted when an alert is resolved"""
    
    def __init__(self, alert_id: str, resolved_by: Optional[str] = None, resolution_note: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="alert.resolved",
            source_service="notification-service",
            data={
                "alert_id": alert_id,
                "resolved_by": resolved_by,
                "resolution_note": resolution_note
            },
            **kwargs
        )

class NotificationSentEvent(BaseEvent):
    """Event emitted when a notification is sent"""
    
    def __init__(self, notification_id: str, channel: str, recipient: str, success: bool, **kwargs):
        super().__init__(
            event_type="notification.sent",
            source_service="notification-service",
            data={
                "notification_id": notification_id,
                "channel": channel,  # "email", "sms", "websocket"
                "recipient": recipient,
                "success": success
            },
            **kwargs
        )

class NotificationRuleTriggeredEvent(BaseEvent):
    """Event emitted when a notification rule is triggered"""
    
    def __init__(self, rule_id: str, trigger_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="notification.rule.triggered",
            source_service="notification-service",
            data={
                "rule_id": rule_id,
                "trigger_data": trigger_data
            },
            **kwargs
        )

class UserConnectedEvent(BaseEvent):
    """Event emitted when user connects to WebSocket"""
    
    def __init__(self, user_id: str, connection_id: str, **kwargs):
        super().__init__(
            event_type="user.connected",
            source_service="notification-service",
            data={
                "user_id": user_id,
                "connection_id": connection_id
            },
            **kwargs
        )

class UserDisconnectedEvent(BaseEvent):
    """Event emitted when user disconnects from WebSocket"""
    
    def __init__(self, user_id: str, connection_id: str, **kwargs):
        super().__init__(
            event_type="user.disconnected",
            source_service="notification-service",
            data={
                "user_id": user_id,
                "connection_id": connection_id
            },
            **kwargs
        )
