"""
Coordination System Module

Manages agent coordination, consensus building, and task distribution.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import asyncio


class TaskStatus(str, Enum):
    """Status of a coordination task"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CoordinationTask(BaseModel):
    """Task for agent coordination"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    assigned_agents: List[str] = Field(default_factory=list)
    required_roles: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    result: Optional[Any] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class CoordinationSystem:
    """
    Coordination system for managing agent collaboration
    and consensus building
    """
    
    def __init__(self):
        self.tasks: Dict[str, CoordinationTask] = {}
        self.agent_tasks: Dict[str, Set[str]] = {}  # agent_id -> task_ids
        self.consensus_thresholds: Dict[str, float] = {}
    
    def create_task(
        self,
        title: str,
        description: str,
        required_roles: Optional[List[str]] = None,
        priority: int = 0
    ) -> CoordinationTask:
        """Create a new coordination task"""
        task = CoordinationTask(
            title=title,
            description=description,
            required_roles=required_roles or [],
            priority=priority
        )
        self.tasks[task.task_id] = task
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if agent_id not in task.assigned_agents:
            task.assigned_agents.append(agent_id)
            task.status = TaskStatus.ASSIGNED
        
        # Track agent tasks
        if agent_id not in self.agent_tasks:
            self.agent_tasks[agent_id] = set()
        self.agent_tasks[agent_id].add(task_id)
        
        return True
    
    def start_task(self, task_id: str) -> bool:
        """Mark task as in progress"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS
        return True
    
    def complete_task(self, task_id: str, result: Any) -> bool:
        """Mark task as completed with result"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.result = result
        task.completed_at = datetime.utcnow()
        return True
    
    def fail_task(self, task_id: str, reason: Optional[str] = None) -> bool:
        """Mark task as failed"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.result = {"error": reason}
        task.completed_at = datetime.utcnow()
        return True
    
    def get_agent_tasks(self, agent_id: str, 
                        status: Optional[TaskStatus] = None) -> List[CoordinationTask]:
        """Get all tasks for an agent, optionally filtered by status"""
        task_ids = self.agent_tasks.get(agent_id, set())
        tasks = [self.tasks[tid] for tid in task_ids if tid in self.tasks]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return tasks
    
    def get_pending_tasks(self, required_role: Optional[str] = None) -> List[CoordinationTask]:
        """Get pending tasks, optionally filtered by required role"""
        tasks = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.PENDING
        ]
        
        if required_role:
            tasks = [t for t in tasks if required_role in t.required_roles]
        
        # Sort by priority
        tasks.sort(key=lambda t: t.priority, reverse=True)
        return tasks
    
    async def build_consensus(
        self,
        topic: str,
        agent_responses: Dict[str, Any],
        threshold: float = 0.7
    ) -> Optional[Any]:
        """
        Build consensus from agent responses
        
        Args:
            topic: Topic of consensus
            agent_responses: Dict of agent_id -> response
            threshold: Agreement threshold (0-1)
            
        Returns:
            Consensus result if achieved, None otherwise
        """
        if not agent_responses:
            return None
        
        # Count response frequencies
        response_counts: Dict[Any, int] = {}
        for response in agent_responses.values():
            response_str = str(response)
            response_counts[response_str] = response_counts.get(response_str, 0) + 1
        
        # Check if any response meets threshold
        total = len(agent_responses)
        for response, count in response_counts.items():
            if count / total >= threshold:
                return response
        
        return None
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        
        for task in self.tasks.values():
            stats[task.status.value] += 1
        
        return stats
