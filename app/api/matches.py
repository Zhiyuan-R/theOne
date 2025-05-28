"""
Matching API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User, Match, Profile
from app.schemas.user import MatchResponse
from app.services.ai_matching import ai_matching_service

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/generate-daily-matches")
async def generate_daily_matches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate daily matches for the current user"""
    # Check if user has profile and expectations
    if not current_user.profile:
        raise HTTPException(status_code=400, detail="Please create your profile first")

    if not current_user.expectations:
        raise HTTPException(status_code=400, detail="Please set your expectations first")

    # Get all other users with complete profiles and expectations
    candidate_users = db.query(User).options(
        joinedload(User.profile).joinedload(Profile.photos),
        joinedload(User.expectations).joinedload(User.expectations.example_images)
    ).filter(
        User.id != current_user.id,
        User.profile.isnot(None),
        User.expectations.isnot(None)
    ).all()

    if not candidate_users:
        raise HTTPException(status_code=404, detail="No potential matches found")

    # Generate matches using AI with enhanced analysis
    matches_data = await ai_matching_service.find_daily_matches(
        current_user, candidate_users, limit=5, include_reasoning=False
    )

    # Save matches to database
    saved_matches = []
    for match_data in matches_data:
        # Check if match already exists today
        existing_match = db.query(Match).filter(
            Match.user_id == current_user.id,
            Match.matched_user_id == match_data["user_id"]
        ).first()

        if not existing_match:
            db_match = Match(
                user_id=current_user.id,
                matched_user_id=match_data["user_id"],
                compatibility_score=match_data["compatibility_score"],
                text_similarity_score=match_data["text_similarity"],
                visual_similarity_score=match_data["visual_similarity"],
                basic_text_similarity=match_data["basic_text_similarity"],
                llm_text_score=match_data["llm_text_score"],
                personality_score=match_data["personality_score"],
                lifestyle_score=match_data["lifestyle_score"],
                emotional_score=match_data["emotional_score"],
                longterm_score=match_data["longterm_score"]
            )
            db.add(db_match)
            saved_matches.append(db_match)

    db.commit()

    return {"message": f"Generated {len(saved_matches)} new matches"}


@router.get("/detailed/{match_id}")
async def get_detailed_match_analysis(
    match_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed compatibility analysis for a specific match"""
    # Get the match
    match = db.query(Match).filter(
        Match.id == match_id,
        Match.user_id == current_user.id
    ).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Get the matched user with profile and expectations
    matched_user = db.query(User).options(
        joinedload(User.profile).joinedload(Profile.photos),
        joinedload(User.expectations).joinedload(User.expectations.example_images)
    ).filter(User.id == match.matched_user_id).first()

    if not matched_user or not matched_user.profile or not matched_user.expectations:
        raise HTTPException(status_code=404, detail="Matched user profile not found")

    # Generate detailed reasoning using AI
    compatibility_scores = {
        "overall_score": match.compatibility_score,
        "text_similarity": match.text_similarity_score,
        "visual_similarity": match.visual_similarity_score,
        "basic_text_similarity": match.basic_text_similarity,
        "llm_text_score": match.llm_text_score,
        "personality_score": match.personality_score,
        "lifestyle_score": match.lifestyle_score,
        "emotional_score": match.emotional_score,
        "longterm_score": match.longterm_score
    }

    reasoning = await ai_matching_service.generate_compatibility_reasoning(
        current_user.profile,
        matched_user.profile,
        current_user.expectations,
        matched_user.expectations,
        compatibility_scores
    )

    return {
        "match_id": match.id,
        "matched_user_id": matched_user.id,
        "compatibility_scores": compatibility_scores,
        "detailed_analysis": reasoning,
        "created_at": match.created_at
    }


@router.get("/daily", response_model=List[MatchResponse])
def get_daily_matches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get today's matches for the current user"""
    matches = db.query(Match).options(
        joinedload(Match.matched_user).joinedload(User.profile).joinedload(Profile.photos)
    ).filter(
        Match.user_id == current_user.id
    ).order_by(Match.compatibility_score.desc()).limit(10).all()

    # Convert to response format
    match_responses = []
    for match in matches:
        match_response = MatchResponse(
            id=match.id,
            matched_user_id=match.matched_user_id,
            compatibility_score=match.compatibility_score,
            text_similarity_score=match.text_similarity_score,
            visual_similarity_score=match.visual_similarity_score,
            is_viewed=match.is_viewed,
            created_at=match.created_at,
            matched_user_profile=match.matched_user.profile if match.matched_user else None
        )
        match_responses.append(match_response)

    return match_responses


@router.put("/{match_id}/view")
def mark_match_as_viewed(
    match_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a match as viewed"""
    match = db.query(Match).filter(
        Match.id == match_id,
        Match.user_id == current_user.id
    ).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.is_viewed = True
    db.commit()

    return {"message": "Match marked as viewed"}


@router.get("/stats")
def get_match_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get matching statistics for the current user"""
    total_matches = db.query(Match).filter(Match.user_id == current_user.id).count()
    viewed_matches = db.query(Match).filter(
        Match.user_id == current_user.id,
        Match.is_viewed == True
    ).count()

    avg_compatibility = db.query(Match).filter(
        Match.user_id == current_user.id
    ).with_entities(Match.compatibility_score).all()

    avg_score = 0.0
    if avg_compatibility:
        avg_score = sum(score[0] for score in avg_compatibility) / len(avg_compatibility)

    return {
        "total_matches": total_matches,
        "viewed_matches": viewed_matches,
        "unviewed_matches": total_matches - viewed_matches,
        "average_compatibility_score": round(avg_score, 3)
    }
