"""
Voting API Router

API endpoints for voting system.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..voting.voting_engine import VoteType, VotingEngine, VoteStatus
from ..api.dependencies import get_voting_engine


router = APIRouter()


class CreateVotingSessionRequest(BaseModel):
    """Request to create voting session"""
    title: str
    description: str
    vote_type: VoteType
    options: List[str]
    duration_minutes: int = 60


class CastVoteRequest(BaseModel):
    """Request to cast a vote"""
    choice: str
    tokens_staked: float = 0.0


class VotingSessionResponse(BaseModel):
    """Voting session response"""
    session_id: str
    title: str
    status: str
    total_votes: int


@router.get("/sessions", response_model=List[VotingSessionResponse])
async def list_sessions(
    status: Optional[str] = None,
    engine: VotingEngine = Depends(get_voting_engine)
):
    """List voting sessions"""
    sessions = engine.sessions.values()
    if status:
        sessions = [s for s in sessions if s.status.value == status]

    return [
        VotingSessionResponse(
            session_id=s.session_id,
            title=s.title,
            status=s.status.value,
            total_votes=len(s.votes)
        ) for s in sessions
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
        duration_minutes=request.duration_minutes
    )

    # Auto-start for now as per typical API usage where creation implies availability
    engine.start_session(session.session_id)

    return VotingSessionResponse(
        session_id=session.session_id,
        title=session.title,
        status=session.status.value,
        total_votes=len(session.votes)
    )


@router.post("/sessions/{session_id}/vote")
async def cast_vote(
    session_id: str,
    request: CastVoteRequest,
    x_user_id: Optional[str] = Header(None),
    engine: VotingEngine = Depends(get_voting_engine)
):
    """Cast a vote in a session"""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header required")

    session = engine.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    vote = engine.cast_vote(
        session_id=session_id,
        user_id=x_user_id,
        choice=request.choice,
        tokens_staked=request.tokens_staked
    )

    if not vote:
        # Determine specific error
        if session.status != VoteStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Session is not active")

        # Check if user already voted
        user_vote_ids = engine.user_votes.get(x_user_id, [])
        for v in session.votes:
            if v.vote_id in user_vote_ids:
                raise HTTPException(status_code=400, detail="User already voted")

        # Check minimum stake
        if request.tokens_staked < session.min_stake:
             raise HTTPException(status_code=400, detail=f"Insufficient stake. Minimum required: {session.min_stake}")

        raise HTTPException(status_code=400, detail="Vote failed")

    return {"status": "voted", "session_id": session_id, "vote_id": vote.vote_id}


@router.get("/sessions/{session_id}/results")
async def get_results(
    session_id: str,
    engine: VotingEngine = Depends(get_voting_engine)
):
    """Get voting session results"""
    session = engine.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # If session is finalized, return results
    if session.status == VoteStatus.FINALIZED and session.results:
        return session.results

    # If session is closed but not finalized, finalize it
    if session.status == VoteStatus.CLOSED:
        results = engine.finalize_session(session_id)
        return results

    # If session is active, return current stats
    stats = engine.get_session_stats(session_id)
    if stats:
        return stats

    return {}
