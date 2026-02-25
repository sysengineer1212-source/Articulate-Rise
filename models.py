"""Data models for MCU-ALTEA 150 Course Structure"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BlockType(str, Enum):
    """Types of content blocks in Rise 360"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    INTERACTION = "interaction"
    LIST = "list"


class ContentElement(BaseModel):
    """Individual content element within a theme"""
    type: BlockType
    title: str
    content: str
    words: Optional[int] = None
    duration_minutes: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    rise_360_id: Optional[str] = None


class Concept(BaseModel):
    """Key concept within a theme"""
    term: str
    definition: str


class Narrative(ContentElement):
    """Narrative element specifications"""
    type: BlockType = BlockType.TEXT
    structure: str = "3-act"  # Introduction, Development, Resolution
    character: str
    concepts_integrated: List[str]
    tone: str = "personal, historical, with narrative tension"


class AcademicText(ContentElement):
    """Academic text element specifications"""
    type: BlockType = BlockType.TEXT
    structure: str = "intro-development-conclusion"
    concepts_count: int = Field(ge=4, le=5)
    references: List[str]
    headings: Dict[str, int]  # Heading level distribution


class VideoScript(ContentElement):
    """Video script element specifications"""
    type: BlockType = BlockType.VIDEO
    duration_minutes: float = 5.0
    structure: str = "intro-development-closing"
    concepts_count: int = Field(le=3)
    examples_count: int = Field(ge=2)
    visuals_count: int
    sections: List[Dict[str, Any]]  # [NARRACIÓN], [VISUAL] sections


class Infographic(ContentElement):
    """Infographic element specifications"""
    type: BlockType = BlockType.IMAGE
    width_px: int = 1200
    height_px: int = 900
    structure: str  # "radial" or "vertical_columns"
    sections_count: int = Field(ge=4, le=6)
    color_palette: List[str]
    elements: List[Dict[str, str]]  # Each element has icon, title, text, formula


class PracticalActivity(ContentElement):
    """Practical activity element specifications"""
    type: BlockType = BlockType.INTERACTION
    duration_minutes: int = 60
    components: List[str]
    rubric_criteria: int = 5
    deliverables: List[str]
    success_criteria: List[str]


class Theme(BaseModel):
    """Theme within a unit (3 themes per unit)"""
    unit_number: int
    theme_number: int
    code: str  # e.g., "1.1"
    title: str
    description: Optional[str] = None
    narrative: Narrative
    concepts: List[Concept] = Field(min_items=5, max_items=5)
    academic_text: AcademicText
    infographic: Infographic
    video_script: VideoScript
    activity: PracticalActivity
    rise_360_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Unit(BaseModel):
    """Unit within the course (5 units total)"""
    unit_number: int
    code: str  # e.g., "UNIDAD 1"
    title: str
    duration_hours: float = 15.0
    themes: List[Theme] = Field(min_items=3, max_items=3)
    synthesis: Optional[str] = None  # 300 words
    integrated_project: Optional[str] = None  # 800-1000 words
    additional_resources: Optional[Dict[str, List[str]]] = None
    formative_evaluation: Optional[List[str]] = None  # 12 questions
    transition_to_next: Optional[str] = None  # 200 words
    rise_360_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Course(BaseModel):
    """Complete course structure"""
    name: str
    code: str
    area: str
    level: str
    language: str
    duration_hours: float
    target_audience: str
    units: List[Unit] = Field(min_items=5, max_items=5)
    competencies: List[Dict[str, str]]
    rise_360_id: Optional[str] = None
    rise_360_url: Optional[str] = None
    created_at: Optional[datetime] = None
    status: str = "draft"  # draft, published, archived


class InsertionLog(BaseModel):
    """Log entry for each content block insertion"""
    timestamp: datetime
    unit_number: int
    theme_number: int
    element_type: BlockType
    element_title: str
    status: str  # success, failed, retried
    rise_360_id: Optional[str] = None
    words: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    duration_seconds: float


class ValidationResult(BaseModel):
    """Result of validation for a content element"""
    element_id: str
    element_type: BlockType
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    metrics: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class CourseCreationReport(BaseModel):
    """Final report of course creation"""
    total_units: int
    total_themes: int
    total_elements: int
    successful_insertions: int
    failed_insertions: int
    validation_results: List[ValidationResult]
    insertion_logs: List[InsertionLog]
    course_url: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None
    metrics: Dict[str, Any] = {}
