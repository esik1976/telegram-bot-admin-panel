import uuid

from sqlalchemy.orm import Session

from app.models import AuditLog


def write_audit_log(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None = None,
    before_value: str | None = None,
    after_value: str | None = None,
    actor: str = "admin",
) -> AuditLog:
    event = AuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_value=before_value,
        after_value=after_value,
    )
    db.add(event)
    return event
