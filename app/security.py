import secrets
import hashlib
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
from .models import Game

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"game_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage using SHA256
    More reliable than bcrypt and no length limits
    """
    # Use SHA256 with multiple rounds for security
    salt = b'highscore_api_salt_2025'  # In production, use random salt per key
    hashed = hashlib.pbkdf2_hmac('sha256', api_key.encode('utf-8'), salt, 100000)
    return hashed.hex()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return hash_api_key(plain_key) == hashed_key


def get_game_by_api_key(db: Session, api_key: str) -> Optional[Game]:
    """Get a game by API key"""
    games = db.query(Game).all()
    for game in games:
        if verify_api_key(api_key, game.api_key_hash):
            return game
    return None


async def verify_api_key_dependency(
    api_key: str = Security(api_key_header),
    db: Session = None
) -> Game:
    """
    FastAPI dependency to verify API key and return the associated game
    Note: This is a placeholder. The actual db dependency will be injected in routes.
    """
    game = get_game_by_api_key(db, api_key)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return game
