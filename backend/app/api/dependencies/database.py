"""Database session dependency."""
from app.core.database.engine import get_db

__all__ = ["get_db"]
