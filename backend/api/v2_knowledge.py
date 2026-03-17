"""
Morpheus v2 API: 大纲 + 知识图谱接口
独立文件，在 main.py 末尾引入。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException

# ── 这些从 main.py 注入 ──
router = APIRouter(prefix="/api/v2", tags=["v2-knowledge"])

_resolve_project = None  # type: ignore
_get_store = None  # type: ignore


def _enum_val(model_class, field_name, value):
    """If field is an Enum, convert string to Enum; otherwise return raw value."""
    field_info = model_class.model_fields.get(field_name)
    if field_info and hasattr(field_info.annotation, '__mro__'):
        for cls in field_info.annotation.__mro__:
            if cls.__name__ == 'Enum' or hasattr(cls, '_value2member_map_'):
                return cls(value)
    return value


def init_v2_routes(resolve_project_fn, get_store_fn):
    """在 main.py 启动时调用，注入依赖。"""
    global _resolve_project, _get_store
    _resolve_project = resolve_project_fn
    _get_store = get_store_fn


def _ensure_project(project_id: str):
    if not _resolve_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return _get_store(project_id)


# ──────────────────────────────
# Volumes (卷)
# ──────────────────────────────

@router.get("/projects/{project_id}/volumes")
async def list_volumes(project_id: str):
    store = _ensure_project(project_id)
    items = store.knowledge.list_volumes(project_id)
    return [v.model_dump() for v in items]


@router.post("/projects/{project_id}/volumes")
async def create_volume(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import Volume
    now = datetime.now()
    v = Volume(
        id=str(uuid4()),
        project_id=project_id,
        volume_number=payload.get("volume_number", 1),
        title=payload.get("title", "未命名卷"),
        summary=payload.get("summary", ""),
        goal=payload.get("goal", ""),
        sort_order=payload.get("sort_order", 0),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_volume(v)
    return v.model_dump()


@router.put("/projects/{project_id}/volumes/{volume_id}")
async def update_volume(project_id: str, volume_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    v = store.knowledge.get_volume(volume_id)
    if not v:
        raise HTTPException(status_code=404, detail="Volume not found")
    for key in ("title", "summary", "goal", "status", "is_locked", "sort_order"):
        if key in payload:
            setattr(v, key, _enum_val(type(v), key, payload[key]))
    store.knowledge.update_volume(v)
    return v.model_dump()


# ──────────────────────────────
# Story Events (事件)
# ──────────────────────────────

@router.get("/projects/{project_id}/events")
async def list_events(project_id: str, volume_id: Optional[str] = None):
    store = _ensure_project(project_id)
    items = store.knowledge.list_events(project_id, volume_id)
    return [e.model_dump() for e in items]


@router.post("/projects/{project_id}/events")
async def create_event(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import StoryEvent
    now = datetime.now()
    e = StoryEvent(
        id=str(uuid4()),
        project_id=project_id,
        volume_id=payload.get("volume_id", ""),
        event_number=payload.get("event_number", 1),
        title=payload.get("title", "未命名事件"),
        summary=payload.get("summary", ""),
        goal=payload.get("goal", ""),
        sort_order=payload.get("sort_order", 0),
        involved_character_ids=payload.get("involved_character_ids", []),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_event(e)
    return e.model_dump()


@router.put("/projects/{project_id}/events/{event_id}")
async def update_event(project_id: str, event_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    e = store.knowledge.get_event(event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    if "involved_character_ids" in payload:
        e.involved_character_ids = payload["involved_character_ids"]
    for key in ("title", "summary", "goal", "status", "is_locked", "sort_order", "volume_id"):
        if key in payload:
            setattr(e, key, _enum_val(type(e), key, payload[key]))
    store.knowledge.update_event(e)
    return e.model_dump()


# ──────────────────────────────
# Characters (角色)
# ──────────────────────────────

@router.get("/projects/{project_id}/characters")
async def list_characters(project_id: str):
    store = _ensure_project(project_id)
    items = store.knowledge.list_characters(project_id)
    return [c.model_dump() for c in items]


@router.post("/projects/{project_id}/characters")
async def create_character(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import CharacterTemplate, CharacterRole
    now = datetime.now()
    c = CharacterTemplate(
        id=str(uuid4()),
        project_id=project_id,
        name=payload.get("name", "未命名"),
        role_type=CharacterRole(payload.get("role_type", "other")),
        gender=payload.get("gender", ""),
        identity=payload.get("identity", ""),
        personality=payload.get("personality", ""),
        appearance=payload.get("appearance", ""),
        background=payload.get("background", ""),
        motivation=payload.get("motivation", ""),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_character(c)
    return c.model_dump()


@router.put("/projects/{project_id}/characters/{char_id}")
async def update_character(project_id: str, char_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    c = store.knowledge.get_character(char_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    from models import CharacterRole
    for key in ("name", "gender", "identity", "personality", "appearance", "background", "is_alive", "motivation"):
        if key in payload:
            setattr(c, key, payload[key])
    if "role_type" in payload:
        c.role_type = CharacterRole(payload["role_type"])
    store.knowledge.update_character(c)
    return c.model_dump()


@router.get("/projects/{project_id}/characters/{char_id}/state")
async def get_character_state(project_id: str, char_id: str):
    store = _ensure_project(project_id)
    s = store.knowledge.get_character_state(char_id)
    if not s:
        return {"character_id": char_id, "state": None}
    return s.model_dump()


@router.put("/projects/{project_id}/characters/{char_id}/state")
async def upsert_character_state(project_id: str, char_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    c = store.knowledge.get_character(char_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    from models import CharacterState
    now = datetime.now()
    s = CharacterState(
        id=str(uuid4()),
        character_id=char_id,
        age=payload.get("age", ""),
        location=payload.get("location", ""),
        abilities=payload.get("abilities", []),
        inventory=payload.get("inventory", []),
        emotional_state=payload.get("emotional_state", ""),
        custom_fields=payload.get("custom_fields", {}),
        as_of_chapter=payload.get("as_of_chapter", 0),
        updated_at=now,
    )
    store.knowledge.upsert_character_state(s)
    return s.model_dump()


# ──────────────────────────────
# Character Relations
# ──────────────────────────────

@router.get("/projects/{project_id}/relations")
async def list_relations(project_id: str):
    store = _ensure_project(project_id)
    items = store.knowledge.list_relations(project_id)
    return [r.model_dump() for r in items]


@router.post("/projects/{project_id}/relations")
async def create_relation(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import CharacterRelation
    now = datetime.now()
    r = CharacterRelation(
        id=str(uuid4()),
        project_id=project_id,
        character_a_id=payload.get("character_a_id", ""),
        character_b_id=payload.get("character_b_id", ""),
        relation_type=payload.get("relation_type", ""),
        strength=payload.get("strength", 5),
        description=payload.get("description", ""),
        turning_point=payload.get("turning_point", ""),
        as_of_chapter=payload.get("as_of_chapter", 0),
        updated_at=now,
    )
    store.knowledge.create_relation(r)
    return r.model_dump()


@router.put("/projects/{project_id}/relations/{rel_id}")
async def update_relation(project_id: str, rel_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    items = store.knowledge.list_relations(project_id)
    r = next((x for x in items if x.id == rel_id), None)
    if not r:
        raise HTTPException(status_code=404, detail="Relation not found")
    for key in ("relation_type", "strength", "description", "turning_point", "as_of_chapter"):
        if key in payload:
            setattr(r, key, payload[key])
    store.knowledge.update_relation(r)
    return r.model_dump()


# ──────────────────────────────
# Cheat Systems (金手指)
# ──────────────────────────────

@router.get("/projects/{project_id}/cheats")
async def list_cheats(project_id: str):
    store = _ensure_project(project_id)
    items = store.knowledge.list_cheats(project_id)
    return [c.model_dump() for c in items]


@router.post("/projects/{project_id}/cheats")
async def create_cheat(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import CheatSystem
    now = datetime.now()
    c = CheatSystem(
        id=str(uuid4()),
        project_id=project_id,
        name=payload.get("name", "未命名"),
        core_logic=payload.get("core_logic", ""),
        limitations=payload.get("limitations", ""),
        upgrade_conditions=payload.get("upgrade_conditions", ""),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_cheat(c)
    return c.model_dump()


@router.get("/projects/{project_id}/cheats/{cheat_id}/state")
async def get_cheat_state(project_id: str, cheat_id: str):
    store = _ensure_project(project_id)
    s = store.knowledge.get_cheat_state(cheat_id)
    if not s:
        return {"cheat_id": cheat_id, "state": None}
    return s.model_dump()


@router.put("/projects/{project_id}/cheats/{cheat_id}/state")
async def upsert_cheat_state(project_id: str, cheat_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import CheatState
    now = datetime.now()
    s = CheatState(
        id=str(uuid4()),
        cheat_id=cheat_id,
        current_level=payload.get("current_level", ""),
        unlocked_features=payload.get("unlocked_features", []),
        usage_status=payload.get("usage_status", {}),
        custom_fields=payload.get("custom_fields", {}),
        as_of_chapter=payload.get("as_of_chapter", 0),
        updated_at=now,
    )
    store.knowledge.upsert_cheat_state(s)
    return s.model_dump()


# ──────────────────────────────
# World Facts (世界观)
# ──────────────────────────────

@router.get("/projects/{project_id}/world-facts")
async def list_world_facts(project_id: str, category: Optional[str] = None):
    store = _ensure_project(project_id)
    items = store.knowledge.list_world_facts(project_id, category)
    return [f.model_dump() for f in items]


@router.post("/projects/{project_id}/world-facts")
async def create_world_fact(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import WorldFact
    now = datetime.now()
    f = WorldFact(
        id=str(uuid4()),
        project_id=project_id,
        category=payload.get("category", "设定"),
        title=payload.get("title", ""),
        content=payload.get("content", ""),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_world_fact(f)
    return f.model_dump()


@router.put("/projects/{project_id}/world-facts/{fact_id}")
async def update_world_fact(project_id: str, fact_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    items = store.knowledge.list_world_facts(project_id)
    f = next((x for x in items if x.id == fact_id), None)
    if not f:
        raise HTTPException(status_code=404, detail="WorldFact not found")
    for key in ("category", "title", "content"):
        if key in payload:
            setattr(f, key, payload[key])
    store.knowledge.update_world_fact(f)
    return f.model_dump()


@router.delete("/projects/{project_id}/world-facts/{fact_id}")
async def delete_world_fact(project_id: str, fact_id: str):
    store = _ensure_project(project_id)
    store.knowledge.delete_world_fact(fact_id)
    return {"status": "deleted"}


# ──────────────────────────────
# Foreshadowings (伏笔)
# ──────────────────────────────

@router.get("/projects/{project_id}/foreshadowings")
async def list_foreshadowings(project_id: str, status: Optional[str] = None):
    store = _ensure_project(project_id)
    items = store.knowledge.list_foreshadowings(project_id, status)
    return [f.model_dump() for f in items]


@router.post("/projects/{project_id}/foreshadowings")
async def create_foreshadowing(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import Foreshadowing
    now = datetime.now()
    f = Foreshadowing(
        id=str(uuid4()),
        project_id=project_id,
        planted_chapter=payload.get("planted_chapter", 0),
        description=payload.get("description", ""),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_foreshadowing(f)
    return f.model_dump()


@router.put("/projects/{project_id}/foreshadowings/{fs_id}")
async def update_foreshadowing(project_id: str, fs_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    items = store.knowledge.list_foreshadowings(project_id)
    f = next((x for x in items if x.id == fs_id), None)
    if not f:
        raise HTTPException(status_code=404, detail="Foreshadowing not found")
    for key in ("status", "collected_chapter", "collection_description"):
        if key in payload:
            setattr(f, key, _enum_val(type(f), key, payload[key]))
    store.knowledge.update_foreshadowing(f)
    return f.model_dump()


# ──────────────────────────────
# Open Threads (未完结线索)
# ──────────────────────────────

@router.get("/projects/{project_id}/threads")
async def list_threads(project_id: str, status: Optional[str] = None):
    store = _ensure_project(project_id)
    items = store.knowledge.list_threads(project_id, status)
    return [t.model_dump() for t in items]


@router.post("/projects/{project_id}/threads")
async def create_thread(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import OpenThread
    now = datetime.now()
    t = OpenThread(
        id=str(uuid4()),
        project_id=project_id,
        title=payload.get("title", ""),
        description=payload.get("description", ""),
        priority=payload.get("priority", "normal"),
        opened_chapter=payload.get("opened_chapter", 0),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_thread(t)
    return t.model_dump()


@router.put("/projects/{project_id}/threads/{thread_id}")
async def update_thread(project_id: str, thread_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    items = store.knowledge.list_threads(project_id)
    t = next((x for x in items if x.id == thread_id), None)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    for key in ("title", "description", "priority", "closed_chapter", "status"):
        if key in payload:
            setattr(t, key, _enum_val(type(t), key, payload[key]))
    store.knowledge.update_thread(t)
    return t.model_dump()


# ──────────────────────────────
# Consistency Rules (矛盾检测)
# ──────────────────────────────

@router.get("/projects/{project_id}/rules")
async def list_rules(project_id: str):
    store = _ensure_project(project_id)
    items = store.knowledge.list_rules(project_id)
    return [r.model_dump() for r in items]


@router.post("/projects/{project_id}/rules")
async def create_rule(project_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    from models import ConsistencyRule
    now = datetime.now()
    r = ConsistencyRule(
        id=str(uuid4()),
        project_id=project_id,
        rule_type=payload.get("rule_type", ""),
        target=payload.get("target", ""),
        condition=payload.get("condition", ""),
        created_at=now,
        updated_at=now,
    )
    store.knowledge.create_rule(r)
    return r.model_dump()


@router.patch("/projects/{project_id}/rules/{rule_id}/toggle")
async def toggle_rule(project_id: str, rule_id: str, payload: Dict[str, Any]):
    store = _ensure_project(project_id)
    is_active = payload.get("is_active", True)
    store.knowledge.toggle_rule(rule_id, is_active)
    return {"status": "updated", "is_active": is_active}


# ──────────────────────────────
# Dashboard: 知识图谱总览
# ──────────────────────────────

@router.get("/projects/{project_id}/knowledge-summary")
async def knowledge_summary(project_id: str):
    """返回知识图谱的全局统计，用于前端仪表盘。"""
    store = _ensure_project(project_id)
    return {
        "volumes": len(store.knowledge.list_volumes(project_id)),
        "events": len(store.knowledge.list_events(project_id)),
        "characters": len(store.knowledge.list_characters(project_id)),
        "relations": len(store.knowledge.list_relations(project_id)),
        "cheats": len(store.knowledge.list_cheats(project_id)),
        "world_facts": len(store.knowledge.list_world_facts(project_id)),
        "foreshadowings_planted": len(store.knowledge.list_foreshadowings(project_id, "planted")),
        "foreshadowings_collected": len(store.knowledge.list_foreshadowings(project_id, "collected")),
        "threads_open": len(store.knowledge.list_threads(project_id, "open")),
        "rules": len(store.knowledge.list_rules(project_id)),
    }
