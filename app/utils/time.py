from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current UTC time with tzinfo set."""
    return datetime.now(timezone.utc)
