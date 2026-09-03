from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel


class AuditEvent(BaseModel):
    event_id: str
    action_id: str
    event: str
    status: str
    message: str
    timestamp: str


audit_log: list[AuditEvent] = []


def record_event(
    action_id: str,
    event: str,
    status: str,
    message: str,
):
    audit_event = AuditEvent(
        event_id=f"evt_{uuid4().hex[:12]}",
        action_id=action_id,
        event=event,
        status=status,
        message=message,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    audit_log.append(audit_event)

    return audit_event


def get_events(action_id: str):
    return [
        event
        for event in audit_log
        if event.action_id == action_id
    ]
