"""
Voting API Router

API endpoints for voting system.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from ..voting.voting_engine import VoteType, VotingEngine
from .dependencies import get_voting_engine


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
    voting_engine: VotingEngine = Depends(get_voting_engine)
):
    """List voting sessions"""
    # Placeholder - integrate with actual voting system
    return []


@router.post("/sessions", response_model=VotingSessionResponse)
async def create_session(
    request: CreateVotingSessionRequest,
    voting_engine: VotingEngine = Depends(get_voting_engine)
):
    """Create a new voting session"""
    session = voting_engine.create_session(
        title=request.title,
        description=request.description,
        vote_type=request.vote_type,
        options=request.options,
        duration_minutes=request.duration_minutes
    )

    return VotingSessionResponse(
        session_id=session.session_id,
        title=session.title,
        status=session.status.value,
        total_votes=len(session.votes)
    )


@router.post("/sessions/{session_id}/vote")
async def cast_vote(session_id: str, request: CastVoteRequest):
    """Cast a vote in a session"""
    # Placeholder - integrate with actual voting system
    return {"status": "voted", "session_id": session_id}


@router.get("/sessions/{session_id}/results")
async def get_results(session_id: str):
    """Get voting session results"""
    # Placeholder - integrate with actual voting system
    raise HTTPException(status_code=404, detail="Session not found")
