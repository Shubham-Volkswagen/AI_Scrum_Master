from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

IssueType = Literal["Epic", "Feature", "Story", "Task", "Bug"]

class MissingDetail(BaseModel):
    field: str
    question: str
    blocking: bool = True

class Traceability(BaseModel):
    source_type: str
    source_id: str
    source_excerpt: Optional[str] = None
    rationale: str

class Dependency(BaseModel):
    depends_on_local_id: str
    dependency_type: Literal["BLOCKS", "REQUIRES", "RELATES_TO"] = "REQUIRES"
    reason: str

class BacklogItem(BaseModel):
    local_id: str
    issue_type: IssueType
    summary: str
    description: str
    parent_local_id: Optional[str] = None
    sad_section_id: Optional[str] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    definition_of_done: List[str] = Field(default_factory=list)
    story_points: Optional[int] = None
    estimation_confidence: Optional[float] = None
    estimation_reason: Optional[str] = None
    priority: Literal["Highest", "High", "Medium", "Low"] = "Medium"
    architecture_layer: Optional[str] = None
    dependencies: List[Dependency] = Field(default_factory=list)
    traceability: List[Traceability] = Field(default_factory=list)
    readiness_status: Literal["READY", "NEEDS_CLARIFICATION", "BLOCKED"] = "NEEDS_CLARIFICATION"
    missing_details: List[MissingDetail] = Field(default_factory=list)

class BacklogPackage(BaseModel):
    normalized_demand: str
    intake_mode: str
    clarification_questions: List[str] = Field(default_factory=list)
    items: List[BacklogItem]
    assumptions: List[str] = Field(default_factory=list)

class SprintAssignment(BaseModel):
    ticket_local_id: str
    sprint_id: str
    placement_reason: str
    capacity_before: float
    capacity_after: float
    dependency_order: int
    requires_human_confirmation: bool = False

class ChangeRecommendation(BaseModel):
    raw_text: str
    duplicate_id: Optional[str] = None
    similarity_score: float = 0.0
    suggested_parent_id: Optional[str] = None
    suggested_sprint_id: Optional[str] = None
    explanation: str
    requires_human_confirmation: bool = True
