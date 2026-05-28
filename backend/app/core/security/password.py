"""
Utilitário de hash de senhas usando bcrypt.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Retorna o hash bcrypt da senha."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha bate com o hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)
