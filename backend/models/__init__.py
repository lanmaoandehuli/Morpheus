from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Layer(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class ProjectStatus(str, Enum):
    INIT = "init"
    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"


class ChapterStatus(str, Enum):
    DRAFT = "draft"
    REVIEWING = "reviewing"
    REVISED = "revised"
    APPROVED = "approved"


class AgentRole(str, Enum):
    DIRECTOR = "director"
    SETTER = "setter"
    CONTINUITY = "continuity"
    STYLIST = "stylist"
    ARBITER = "arbiter"


class MemoryItem(BaseModel):
    id: str
    layer: Layer
    source_path: str
    summary: str
    content: str
    embedding: Optional[List[float]] = None
    entities: List[str] = Field(default_factory=list)
    time_span: Optional[Dict[str, str]] = None
    importance: int = Field(default=5, ge=1, le=10)
    recency: int = Field(default=1, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityState(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    attrs: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    first_seen_chapter: int = 0
    last_seen_chapter: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class EventEdge(BaseModel):
    event_id: str
    subject: str
    relation: str
    object: Optional[str] = None
    chapter: int
    timestamp: Optional[datetime] = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class Conflict(BaseModel):
    id: str
    severity: Severity
    rule_id: str
    evidence_paths: List[str] = Field(default_factory=list)
    reason: str
    suggested_fix: Optional[str] = None
    chapter_id: int
    resolved: bool = False
    exempted: bool = False
    resolution: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class Project(BaseModel):
    id: str
    name: str
    genre: str
    style: str
    template_id: Optional[str] = None
    target_length: int = 300000
    taboo_constraints: List[str] = Field(default_factory=list)
    status: ProjectStatus = ProjectStatus.INIT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChapterPlan(BaseModel):
    id: str
    chapter_id: int
    title: str
    goal: str
    beats: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    foreshadowing: List[str] = Field(default_factory=list)
    callback_targets: List[str] = Field(default_factory=list)
    role_goals: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class Chapter(BaseModel):
    id: str
    project_id: str
    chapter_number: int
    title: str
    goal: str
    plan: Optional[ChapterPlan] = None
    draft: Optional[str] = None
    final: Optional[str] = None
    status: ChapterStatus = ChapterStatus.DRAFT
    word_count: int = 0
    volume_id: Optional[str] = None
    event_id: Optional[str] = None
    first_pass_ok: Optional[bool] = None
    memory_hit_count: int = 0
    p0_conflict_count: int = 0
    summary: Optional[str] = None
    conflicts: List[Conflict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AgentDecision(BaseModel):
    id: str
    agent_role: AgentRole
    chapter_id: int
    input_refs: List[str] = Field(default_factory=list)
    decision_text: str
    rejected_options: List[str] = Field(default_factory=list)
    reasoning: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentTrace(BaseModel):
    id: str
    chapter_id: int
    decisions: List[AgentDecision] = Field(default_factory=list)
    memory_hits: List[Dict[str, Any]] = Field(default_factory=list)
    conflicts_detected: List[Conflict] = Field(default_factory=list)
    final_draft: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class SearchResult(BaseModel):
    item_id: str
    layer: Layer
    source_path: str
    summary: str
    score: float
    evidence: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HybridSearchResult(BaseModel):
    results: List[SearchResult]
    total_score: float
    sources: Dict[str, int] = Field(default_factory=dict)


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REWRITE = "rewrite"
    EXEMPT = "exempt"
    RESCAN = "rescan"


class ReviewRecord(BaseModel):
    id: str
    chapter_id: int
    action: ReviewAction
    comment: str = ""
    conflicts_resolved: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class Metrics(BaseModel):
    chapter_generation_time: float = 0
    search_time: float = 0
    conflict_check_time: float = 0
    conflicts_per_chapter: float = 0
    p0_ratio: float = 0
    exemption_rate: float = 0
    recall_hit_rate: float = 0
    false_recall_rate: float = 0
    rework_rate: float = 0
    first_pass_rate: float = 0
    chapter_id: Optional[int] = None
    project_id: Optional[str] = None
    recorded_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────
# Morpheus v2: 大纲 + 知识图谱
# ──────────────────────────────────────────────

class VolumeStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class EventStatus(str, Enum):
    PENDING = "pending"
    WRITING = "writing"
    COMPLETED = "completed"


class StorylineStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class ForeshadowStatus(str, Enum):
    PLANTED = "planted"
    COLLECTED = "collected"


class ThreadStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    ABANDONED = "abandoned"


class ThreadPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# ── 大纲 ──

class Volume(BaseModel):
    id: str
    project_id: str
    volume_number: int
    title: str
    summary: Optional[str] = ""
    goal: Optional[str] = ""
    status: VolumeStatus = VolumeStatus.ACTIVE
    is_locked: bool = False
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StoryEvent(BaseModel):
    id: str
    project_id: str
    volume_id: str
    storyline_id: Optional[str] = None  # 多线叙事：所属故事线
    event_number: int
    title: str
    summary: Optional[str] = ""
    goal: Optional[str] = ""
    status: EventStatus = EventStatus.PENDING
    is_locked: bool = False
    sort_order: int = 0
    involved_character_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Storyline(BaseModel):
    """多线叙事：同一卷内的并行情节线（如江湖线、宫廷线、感情线）"""
    id: str
    project_id: str
    volume_id: str
    title: str
    color: str = "#6b7280"          # 故事线颜色，用于UI区分
    description: Optional[str] = ""
    status: StorylineStatus = StorylineStatus.ACTIVE
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ── 角色系统 ──

class CharacterRole(str, Enum):
    PROTAGONIST = "protagonist"  # 主角
    SUPPORTING = "supporting"    # 配角
    MINION = "minion"            # 小喽啰
    VILLAIN = "villain"          # 大反派
    OTHER = "other"              # 其他

class CharacterTemplate(BaseModel):
    id: str
    project_id: str
    name: str
    role_type: CharacterRole = CharacterRole.OTHER
    gender: Optional[str] = ""
    identity: Optional[str] = ""
    personality: Optional[str] = ""
    appearance: Optional[str] = ""
    background: Optional[str] = ""
    motivation: Optional[str] = ""  # 核心动机（反派必填）
    is_alive: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CharacterState(BaseModel):
    id: str
    character_id: str
    age: Optional[str] = ""
    status: Optional[str] = ""  # 健康/受伤/中毒/修炼中等
    location: Optional[str] = ""
    abilities: List[str] = Field(default_factory=list)
    weapons: List[str] = Field(default_factory=list)
    inventory: List[str] = Field(default_factory=list)
    emotional_state: Optional[str] = ""
    battle_power: Optional[str] = ""  # 战力描述，如"筑基初期""三品武者"
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    as_of_chapter: int = 0
    updated_at: datetime = Field(default_factory=datetime.now)


class CharacterRelation(BaseModel):
    id: str
    project_id: str
    character_a_id: str
    character_b_id: str
    relation_type: str
    strength: int = Field(default=5, ge=1, le=10)
    description: Optional[str] = ""
    turning_point: Optional[str] = ""
    as_of_chapter: int = 0
    updated_at: datetime = Field(default_factory=datetime.now)


# ── 金手指系统 ──

class CheatSystem(BaseModel):
    id: str
    project_id: str
    name: str
    core_logic: str
    limitations: Optional[str] = ""
    upgrade_conditions: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CheatState(BaseModel):
    id: str
    cheat_id: str
    current_level: Optional[str] = ""
    unlocked_features: List[str] = Field(default_factory=list)
    usage_status: Dict[str, Any] = Field(default_factory=dict)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    as_of_chapter: int = 0
    updated_at: datetime = Field(default_factory=datetime.now)


# ── 世界观 / 伏笔 / 线索 / 规则 ──

class WorldFact(BaseModel):
    id: str
    project_id: str
    category: str
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Foreshadowing(BaseModel):
    id: str
    project_id: str
    planted_chapter: int
    description: str
    status: ForeshadowStatus = ForeshadowStatus.PLANTED
    collected_chapter: Optional[int] = None
    collection_description: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class OpenThread(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    priority: ThreadPriority = ThreadPriority.NORMAL
    opened_chapter: int
    closed_chapter: Optional[int] = None
    status: ThreadStatus = ThreadStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ConsistencyRule(BaseModel):
    id: str
    project_id: str
    rule_type: str
    target: str
    condition: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ── 写作风格 ──

class WritingStylePreset(BaseModel):
    """预设写作风格"""
    id: str
    name: str
    description: str
    # 语气
    tone: str = "中性"            # 轻松/幽默/严肃/压抑/中性
    # 句式
    sentence_length: str = "交替" # 长句/短句/交替
    # 词汇
    vocabulary: str = "白话"      # 古风/白话/网络
    # 人称
    pov: str = "第三人称限定"    # 第一人称/第三人称全知/第三人称限定
    # 对话占比
    dialogue_ratio: str = "均衡"   # 对话多/叙述多/均衡
    # 爽点偏好
    excitement_preference: str = ""  # 空=按类型自动


WRITING_STYLE_PRESETS: List[WritingStylePreset] = [
    WritingStylePreset(
        id="light", name="轻松爽文", description="节奏快、爽点多、打脸频繁",
        tone="轻松", sentence_length="短句", vocabulary="白话", pov="第三人称限定",
        dialogue_ratio="对话多", excitement_preference="爽文"),
    WritingStylePreset(
        id="humor", name="幽默喜剧", description="对白风趣、吐槽密集、反转多",
        tone="幽默", sentence_length="交替", vocabulary="网络", pov="第三人称限定",
        dialogue_ratio="对话多", excitement_preference="幽默"),
    WritingStylePreset(
        id="serious", name="严肃正剧", description="文笔考究、冲突深沉、节奏稳健",
        tone="严肃", sentence_length="长句", vocabulary="白话", pov="第三人称全知",
        dialogue_ratio="叙述多", excitement_preference="正剧"),
    WritingStylePreset(
        id="ancient", name="古风武侠", description="古韵词汇、章回体风格、诗意描写",
        tone="中性", sentence_length="长句", vocabulary="古风", pov="第三人称全知",
        dialogue_ratio="均衡", excitement_preference="武侠"),
    WritingStylePreset(
        id="网文通用", name="网文通用", description="起点风、快节奏、高潮密集",
        tone="轻松", sentence_length="短句", vocabulary="白话", pov="第三人称限定",
        dialogue_ratio="对话多", excitement_preference="爽文"),
]
