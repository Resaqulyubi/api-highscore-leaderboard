from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta
import traceback
from . import schemas, models
from .database import get_db
from .security import (
    generate_api_key,
    hash_api_key,
    get_game_by_api_key,
    api_key_header
)
from .rate_limiter import limiter, RATE_LIMITS
from .config import settings

router = APIRouter(prefix="/api/v1", tags=["HighScore API"])


# ==================== Game Endpoints ====================

@router.post(
    "/games",
    response_model=schemas.GameResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new game",
    description="Register a new game and receive an API key. Save the API key as it's only shown once!"
)
@limiter.limit(RATE_LIMITS["create_game"])
async def create_game(
    request: Request,
    game: schemas.GameCreate,
    db: Session = Depends(get_db)
):
    """Create a new game and generate API key"""
    try:
        # Generate API key
        api_key = generate_api_key()
        api_key_hash = hash_api_key(api_key)
        
        # Create game
        db_game = models.Game(
            name=game.name,
            description=game.description,
            api_key_hash=api_key_hash
        )
        
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
        
        # Return game info with plain API key (only shown once)
        return schemas.GameResponse(
            id=db_game.id,
            name=db_game.name,
            description=db_game.description,
            api_key=api_key,
            created_at=db_game.created_at
        )
    except Exception as e:
        db.rollback()
        print(f"Error creating game: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create game: {str(e)}"
        )


@router.get(
    "/games/me",
    response_model=schemas.GameInfo,
    summary="Get current game info",
    description="Get information about the game associated with the provided API key"
)
@limiter.limit(RATE_LIMITS["default"])
async def get_current_game(
    request: Request,
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
):
    """Get current game info using API key"""
    game = get_game_by_api_key(db, api_key)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return schemas.GameInfo(
        id=game.id,
        name=game.name,
        description=game.description,
        created_at=game.created_at
    )


# ==================== Score Endpoints ====================

@router.post(
    "/scores",
    response_model=schemas.ScoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a score",
    description="Submit a new score for a player in your game"
)
@limiter.limit(RATE_LIMITS["submit_score"])
async def submit_score(
    request: Request,
    score_data: schemas.ScoreCreate,
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
):
    """Submit a new score"""
    # Verify API key and get game
    game = get_game_by_api_key(db, api_key)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Create score
    db_score = models.Score(
        game_id=game.id,
        player_name=score_data.player_name,
        score=score_data.score,
        game_metadata=score_data.game_metadata
    )
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    return db_score


# ==================== Leaderboard Endpoints ====================

def get_date_filter(period: Optional[str]) -> Optional[datetime]:
    """Get datetime filter based on period"""
    if not period:
        return None
    
    now = datetime.utcnow()
    
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        return now - timedelta(days=7)
    elif period == "month":
        return now - timedelta(days=30)
    elif period == "year":
        return now - timedelta(days=365)
    else:
        return None


@router.get(
    "/leaderboard",
    response_model=schemas.LeaderboardResponse,
    summary="Get leaderboard",
    description="Get leaderboard for your game. Supports filtering by time period and limiting results."
)
@limiter.limit(RATE_LIMITS["get_leaderboard"])
async def get_leaderboard(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="Number of top scores to return"),
    period: Optional[str] = Query(None, description="Time period: 'today', 'week', 'month', 'year', or none for all-time"),
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
):
    """Get leaderboard for the game"""
    # Verify API key and get game
    game = get_game_by_api_key(db, api_key)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Build query
    query = db.query(
        models.Score.player_name,
        func.max(models.Score.score).label('best_score'),
        func.max(models.Score.created_at).label('latest_date')
    ).filter(models.Score.game_id == game.id)
    
    # Apply time filter if specified
    date_filter = get_date_filter(period)
    if date_filter:
        query = query.filter(models.Score.created_at >= date_filter)
    
    # Group by player and order by score
    query = query.group_by(models.Score.player_name).order_by(desc('best_score')).limit(limit)
    
    results = query.all()
    
    # Build leaderboard entries with ranks
    entries = [
        schemas.LeaderboardEntry(
            rank=idx + 1,
            player_name=result.player_name,
            score=result.best_score,
            created_at=result.latest_date
        )
        for idx, result in enumerate(results)
    ]
    
    # Get total entries count
    total_query = db.query(func.count(func.distinct(models.Score.player_name))).filter(
        models.Score.game_id == game.id
    )
    if date_filter:
        total_query = total_query.filter(models.Score.created_at >= date_filter)
    
    total_entries = total_query.scalar()
    
    return schemas.LeaderboardResponse(
        game_id=game.id,
        game_name=game.name,
        entries=entries,
        total_entries=total_entries,
        period=period
    )


# ==================== Player Statistics Endpoints ====================

@router.get(
    "/players/{player_name}/stats",
    response_model=schemas.PlayerStats,
    summary="Get player statistics",
    description="Get detailed statistics for a specific player in your game"
)
@limiter.limit(RATE_LIMITS["player_stats"])
async def get_player_stats(
    request: Request,
    player_name: str,
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific player"""
    # Verify API key and get game
    game = get_game_by_api_key(db, api_key)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Get player scores
    player_scores = db.query(models.Score).filter(
        models.Score.game_id == game.id,
        models.Score.player_name == player_name
    ).all()
    
    if not player_scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player '{player_name}' not found"
        )
    
    # Calculate statistics
    scores = [s.score for s in player_scores]
    best_score = max(scores)
    worst_score = min(scores)
    average_score = sum(scores) / len(scores)
    
    # Get player rank (how many players have a better best score)
    rank_query = db.query(func.count(func.distinct(models.Score.player_name))).filter(
        models.Score.game_id == game.id,
        models.Score.player_name != player_name
    ).filter(
        models.Score.score > best_score
    )
    better_players = rank_query.scalar()
    rank = better_players + 1
    
    # Get first and last played dates
    dates = [s.created_at for s in player_scores]
    first_played = min(dates)
    last_played = max(dates)
    
    return schemas.PlayerStats(
        player_name=player_name,
        game_id=game.id,
        total_scores=len(player_scores),
        best_score=best_score,
        average_score=round(average_score, 2),
        worst_score=worst_score,
        rank=rank,
        first_played=first_played,
        last_played=last_played
    )


# ==================== Health Check ====================

@router.get(
    "/health",
    response_model=schemas.MessageResponse,
    summary="Health check",
    description="Check if the API is running"
)
@limiter.limit(RATE_LIMITS["health"])
async def health_check(request: Request):
    """Health check endpoint"""
    return schemas.MessageResponse(message="HighScore API is running!")
