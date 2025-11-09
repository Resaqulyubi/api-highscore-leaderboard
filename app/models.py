from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Game(Base):
    """Game model - represents a game using the leaderboard API"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    api_key_hash = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scores = relationship("Score", back_populates="game", cascade="all, delete-orphan")


class Score(Base):
    """Score model - represents a player's score in a game"""
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    player_name = Column(String(255), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    game_metadata = Column(JSON, nullable=True)  # Store additional game-specific data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    game = relationship("Game", back_populates="scores")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_game_score', 'game_id', 'score'),
        Index('idx_game_player', 'game_id', 'player_name'),
        Index('idx_game_created', 'game_id', 'created_at'),
    )
