import secrets

import bcrypt


class InvalidTokenError(Exception):
    """Raised when a JWT cannot be decoded or verified."""


class TokenExpiredError(InvalidTokenError):
    """Raised when a JWT has expired."""


BCRYPT_ROUNDS = 14


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    )
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def generate_secure_token() -> str:
    return secrets.token_hex(32)
