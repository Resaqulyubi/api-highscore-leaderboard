from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from .config import settings


# Game Schemas
class GameCreate(BaseModel):
    """Schema for creating a new game"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=settings.max_game_name_length,
        description="Game name"
    )
    description: Optional[str] = Field(
        None, 
        max_length=settings.max_description_length,
        description="Game description"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize game name"""
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for empty after strip
        if not v:
            raise ValueError("Game name cannot be empty or whitespace only")
        
        # Check for valid characters (alphanumeric, spaces, and common punctuation)
        if not re.match(r'^[\w\s\-.,!?()]+$', v):
            raise ValueError("Game name contains invalid characters")
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize description"""
        if v is not None:
            v = v.strip()
            # Allow empty descriptions
            if v and not re.match(r'^[\w\s\-.,!?()"\':;]+$', v):
                raise ValueError("Description contains invalid characters")
        return v


class GameResponse(BaseModel):
    """Schema for game response with API key (only shown once)"""
    id: int
    name: str
    description: Optional[str]
    api_key: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GameInfo(BaseModel):
    """Schema for game info (without API key)"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Score Schemas
class ScoreCreate(BaseModel):
    """Schema for creating/submitting a new score"""
    player_name: str = Field(
        ..., 
        min_length=1, 
        max_length=settings.max_player_name_length,
        description="Player identifier/name"
    )
    score: int = Field(
        ..., 
        ge=0,
        le=settings.max_score_value,
        description="Score value (must be non-negative)"
    )
    game_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional game-specific data"
    )
    
    @field_validator('player_name')
    @classmethod
    def validate_player_name(cls, v: str) -> str:
        """Validate and sanitize player name"""
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for empty after strip
        if not v:
            raise ValueError("Player name cannot be empty or whitespace only")
        
        # Check for valid characters
        if not re.match(r'^[\w\s\-._@]+$', v):
            raise ValueError("Player name contains invalid characters. Allowed: letters, numbers, spaces, -, _, ., @")
        
        return v
    
    @field_validator('game_metadata')
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate metadata size and content"""
        if v is not None:
            # Check metadata size
            import json
            metadata_str = json.dumps(v)
            if len(metadata_str) > settings.max_metadata_size:
                raise ValueError(f"Metadata too large. Maximum size is {settings.max_metadata_size} bytes")
            
            # Validate keys are strings
            for key in v.keys():
                if not isinstance(key, str):
                    raise ValueError("Metadata keys must be strings")
                if not re.match(r'^[\w\-_]+$', key):
                    raise ValueError(f"Invalid metadata key: {key}. Only alphanumeric, -, _ allowed")
        
        return v


class ScoreResponse(BaseModel):
    """Schema for score response"""
    id: int
    game_id: int
    player_name: str
    score: int
    game_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    """Schema for a single leaderboard entry"""
    rank: int
    player_name: str
    score: int
    created_at: datetime


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response"""
    game_id: int
    game_name: str
    entries: List[LeaderboardEntry]
    total_entries: int
    period: Optional[str] = None


# Player Statistics Schemas
class PlayerStats(BaseModel):
    """Schema for player statistics"""
    player_name: str
    game_id: int
    total_scores: int
    best_score: int
    average_score: float
    worst_score: int
    rank: Optional[int] = None
    first_played: datetime
    last_played: datetime


# General Response Schemas
class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
