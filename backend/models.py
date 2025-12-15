"""
Database Models

Defines the database schema for the application.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
import uuid
import enum

from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    wallet_address = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, default=UserRole.USER.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    votes = relationship("Vote", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    progress = relationship("UserProgress", uselist=False, back_populates="user")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    config = Column(JSON, nullable=True)

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=True)
    url = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_timestamp = Column(DateTime, default=datetime.utcnow)

    # Enriched data
    sentiment = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)
    priority_score = Column(Float, default=0.0)

class Vote(Base):
    __tablename__ = "votes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    session_id = Column(String, index=True, nullable=False)
    vote_type = Column(String, nullable=False)
    choice = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="votes")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    tier = Column(String, nullable=False)
    points = Column(Integer, default=0)
    icon = Column(String, nullable=True)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    achievement_id = Column(String, ForeignKey("achievements.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")

class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    points = Column(Integer, default=0)
    tier = Column(String, default="Bronze")
    streak_days = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress")
