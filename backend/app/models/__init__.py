"""Importa todos os models para o Alembic autogenerate funcionar."""
from app.models.user import User
from app.models.message import Message
from app.models.response import Response
from app.models.log import Log
from app.models.setting import Setting

__all__ = ["User", "Message", "Response", "Log", "Setting"]
