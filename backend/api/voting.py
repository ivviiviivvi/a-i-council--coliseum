"""
Voting API Router

API endpoints for voting system.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Any
from pydantic import BaseModel

from ..voting.voting_engine import VotingEngine, VoteType, VoteStatus, VotingSession
from .dependencies import get_voting_engine


router = APIRouter()


class CreateVotingSessionRequest(BaseModel):
    """Request to create voting session"""
    title: str
    description: str
    vote_type: VoteType
    options: List[Any]
    duration_minutes: int = 60
    min_stake: float = 0.0
    reward_pool: float = 0.0


class CastVoteRequest(BaseModel):
    """Request to cast a vote"""
    user_id: str
    choice: Any
    weight: float = 1.0
    tokens_staked: float = 0.0


class VotingSessionResponse(BaseModel):
    """Voting session response"""
    session_id: str
    title: str
    status: VoteStatus
    total_votes: int
    options: List[Any]
    created_at: str  # Serialized datetime


@router.get("/sessions", response_model=List[VotingSessionResponse])
async def list_sessions(
    status: Optional[str] = None,
    engine: VotingEngine = Depends(get_voting_engine)
):
    """List voting sessions"""
    sessions = engine.sessions.values()
    if status:
        sessions = [s for s in sessions if s.status == status]

    return [
        VotingSessionResponse(
            session_id=s.session_id,
            title=s.title,
            status=s.status,
            total_votes=len(s.votes),
            options=s.options,
            created_at=s.created_at.isoformat()
        )
        for s in sessions
    ]


@router.post("/sessions", response_model=VotingSessionResponse)
async def create_session(
    request: CreateVotingSessionRequest,
    engine: VotingEngine = Depends(get_voting_engine)
):
    """Create a new voting session"""
    session = engine.create_session(
        title=request.title,
        description=request.description,
        vote_type=request.vote_type,
        options=request.options,
        duration_minutes=request.duration_minutes,
        min_stake=request.min_stake,
        reward_pool=request.reward_pool
    )

    # Auto-start for now as per simple flow
    engine.start_session(session.session_id)

    return VotingSessionResponse(
        session_id=session.session_id,
        title=session.title,
        status=session.status,
        total_votes=len(session.votes),
        options=session.options,
        created_at=session.created_at.isoformat()
    )


@router.post("/sessions/{session_id}/vote")
async def cast_vote(
    session_id: str,
    request: CastVoteRequest,
    engine: VotingEngine = Depends(get_voting_engine)
):
    """Cast a vote in a session"""
    vote = engine.cast_vote(
        session_id=session_id,
        user_id=request.user_id,
        choice=request.choice,
        weight=request.weight,
        tokens_staked=request.tokens_staked
    )

    if not vote:
        raise HTTPException(status_code=400, detail="Vote failed. Check session status, user eligibility, or duplicate vote.")

    return {
        "status": "voted",
        "session_id": session_id,
        "vote_id": vote.vote_id
    }


@router.get("/sessions/{session_id}/results")
async def get_results(
    session_id: str,
    engine: VotingEngine = Depends(get_voting_engine)
):
    """Get voting session results"""
    # If session is active, we might get partial stats.
    # If closed, we can finalize and get results.

    session = engine.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    stats = engine.get_session_stats(session_id)

    # Check if we have results calculated
    results = session.results
    if not results and session.status in [VoteStatus.CLOSED, VoteStatus.FINALIZED]:
        results = engine.finalize_session(session_id)

    return {
        "stats": stats,
        "results": results
    }
