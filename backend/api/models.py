from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

class NodeType(str, Enum):
    CONVERSATIONAL_AGENT = "conversationalAgent"
    LLM_CHAIN = "llmChain"
    HUMAN_APPROVAL = "humanApproval"
    CUSTOM_TOOL = "customTool"
    CONDITION = "condition"
    LOOP = "loop"

class AgentNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: NodeType = Field(..., description="Type of the node")
    label: str = Field(..., description="Human-readable label")
    data: Dict[str, Any] = Field(..., description="Node configuration data")
    position: Dict[str, float] = Field(..., description="Node position in workflow")

class AgentEdge(BaseModel):
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    condition: Optional[str] = Field(None, description="Conditional logic for edge")

class WorkflowMetadata(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    category: str = Field(..., description="Workflow category")
    tags: List[str] = Field(default=[], description="Workflow tags")
    author: Optional[str] = Field(None, description="Workflow author")

class AgentConfig(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    nodes: List[AgentNode] = Field(..., description="Workflow nodes")
    edges: List[AgentEdge] = Field(..., description="Workflow edges")
    metadata: WorkflowMetadata = Field(..., description="Workflow metadata")
    variables: Dict[str, Any] = Field(default={}, description="Global variables")
    
    @validator('nodes')
    def validate_nodes(cls, v):
        if not v:
            raise ValueError("At least one node is required")
        
        node_ids = [node.id for node in v]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node IDs must be unique")
        
        return v
    
    @validator('edges')
    def validate_edges(cls, v, values):
        if 'nodes' not in values:
            return v
        
        node_ids = {node.id for node in values['nodes']}
        
        for edge in v:
            if edge.source not in node_ids:
                raise ValueError(f"Edge source '{edge.source}' not found in nodes")
            if edge.target not in node_ids:
                raise ValueError(f"Edge target '{edge.target}' not found in nodes")
        
        return v

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"

class ExecutionStep(BaseModel):
    step_id: str
    node_id: str
    status: ExecutionStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    output: Optional[Dict[str, Any]]
    error: Optional[str]

class WorkflowExecution(BaseModel):
    id: str
    agent_id: str
    status: ExecutionStatus
    progress: float = Field(ge=0, le=100)
    current_step: Optional[str]
    steps: List[ExecutionStep]
    started_at: datetime
    completed_at: Optional[datetime]
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

class ApprovalRequest(BaseModel):
    id: str
    execution_id: str
    node_id: str
    message: str
    data: Dict[str, Any]
    timeout: Optional[int] = Field(None, description="Timeout in seconds")
    escalation_email: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]

class ApprovalResponse(BaseModel):
    decision: str = Field(..., regex="^(approve|reject|request_changes)$")
    feedback: Optional[Dict[str, Any]] = Field(default={})
    comments: Optional[str]

class WorkflowTemplate(BaseModel):
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    template_config: AgentConfig = Field(..., description="Template configuration")
    parameters: Dict[str, Any] = Field(default={}, description="Template parameters")
    is_public: bool = Field(default=False, description="Is template public")
    tags: List[str] = Field(default=[], description="Template tags")

class BatchExecution(BaseModel):
    id: str
    executions: List[str] = Field(..., description="List of execution IDs")
    status: ExecutionStatus
    total_executions: int
    completed_executions: int = 0
    failed_executions: int = 0
    created_at: datetime
    completed_at: Optional[datetime]

class CourseCreationRequest(BaseModel):
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    target_audience: str = Field(..., description="Target audience")
    duration: str = Field(..., description="Course duration")
    difficulty_level: str = Field(..., regex="^(beginner|intermediate|advanced)$")
    learning_objectives: List[str] = Field(..., min_items=3, max_items=5)
    topics: List[str] = Field(..., description="Topics to cover")
    assessment_type: str = Field(..., description="Assessment method")
    template_id: Optional[str] = Field(None, description="Template to use")
    custom_requirements: Dict[str, Any] = Field(default={})

class CourseModule(BaseModel):
    number: int
    title: str
    description: str
    learning_objectives: List[str]
    estimated_duration: str
    lessons: List['CourseLesson']

class CourseLesson(BaseModel):
    number: int
    title: str
    content: str
    learning_objectives: List[str]
    activities: List[str]
    assessment: Optional[str]
    resources: List[str] = Field(default=[])

class CourseStructure(BaseModel):
    title: str
    description: str
    overview: str
    learning_objectives: List[str]
    prerequisites: List[str]
    target_audience: str
    duration: str
    modules: List[CourseModule]
    assessment_strategy: str
    resources: List[str] = Field(default=[])

# Update forward references
CourseModule.update_forward_refs()