"""Match service API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from shared.schemas.common import APIResponse
from shared.schemas.pagination import PaginatedResponse, PaginationMeta

from ...schemas.match import (
    BatchMatchRequest,
    BatchMatchResponse,
    MatchDetailResponse,
    MatchScoreRequest,
    MatchScoreResponse,
    SkillGapResponse,
)
from ...schemas.recommendation import (
    JobBasicInfo,
    MatchListResponse,
    RecommendationResponse,
)
from ...services.batch_matcher import BatchMatcher
from ...services.match_service import MatchService
from .dependencies import get_batch_matcher, get_current_user_id, get_match_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("/score", response_model=APIResponse[MatchScoreResponse])
async def score_match(
    request: MatchScoreRequest,
    match_service: MatchService = Depends(get_match_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Score a single profile against a job."""
    score = await match_service.compute_score(request)
    await match_service.save_match(score)
    return APIResponse(data=score)


@router.get("/recommendations/{profile_id}", response_model=APIResponse[MatchListResponse])
async def get_recommendations(
    profile_id: int,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    match_service: MatchService = Depends(get_match_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get top-N match recommendations for a profile."""
    offset = (page - 1) * limit
    matches, total = await match_service.get_profile_matches(
        profile_id=profile_id,
        limit=limit,
        offset=offset,
        min_score=min_score,
    )

    recommendations = []
    for m in matches:
        recommendations.append(RecommendationResponse(
            match_id=m.id,
            job=JobBasicInfo(
                id=m.job_id,
                title="",
                company_name="",
            ),
            overall_score=m.overall_score,
            skills_score=m.skills_score,
            experience_score=m.experience_score,
            matched_skills=m.matched_skills,
            missing_skills=m.missing_skills,
            match_summary=m.match_summary,
            ai_recommendation=m.ai_recommendation,
            rank=m.rank,
            status=m.status,
        ))

    return APIResponse(data=MatchListResponse(
        recommendations=recommendations,
        total=total,
        page=page,
        per_page=limit,
    ))


@router.get("/gaps/{profile_id}/{job_id}", response_model=APIResponse[SkillGapResponse])
async def get_skill_gaps(
    profile_id: int,
    job_id: int,
    match_service: MatchService = Depends(get_match_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get skill gap analysis for a profile+job combination."""
    gaps = await match_service.get_skill_gaps(profile_id, job_id)
    if not gaps:
        raise HTTPException(status_code=404, detail="Match not found")

    return APIResponse(data=SkillGapResponse(
        profile_id=profile_id,
        job_id=job_id,
        matched_skills=gaps.get("matched_skills", []),
        missing_skills=gaps.get("missing_skills", []),
        extra_skills=gaps.get("extra_skills", []),
        match_percentage=gaps.get("match_percentage", 0),
    ))


@router.post("/batch", response_model=APIResponse[BatchMatchResponse])
async def batch_match(
    request: BatchMatchRequest,
    batch_matcher: BatchMatcher = Depends(get_batch_matcher),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Trigger batch matching for a profile or job."""
    result = await batch_matcher.process_batch(request)
    return APIResponse(data=result)
