"""
Morpheus v2: 大纲 + 知识图谱 CRUD
新模块，独立于旧 memory/__init__.py，避免破坏现有功能。
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from models import (
    CheatState,
    CheatSystem,
    CharacterRelation,
    CharacterState,
    CharacterTemplate,
    ConsistencyRule,
    Foreshadowing,
    OpenThread,
    StoryEvent,
    Volume,
    WorldFact,
)


class KnowledgeStore:
    """v2 大纲 + 知识图谱的数据库操作层，复用 MemoryStore 的连接。"""

    def __init__(self, memory_store):
        self._store = memory_store

    def _connection(self):
        return self._store._connection()

    # ──────────────────────────────
    # 表创建（在 MemoryStore._init_db 末尾调用）
    # ──────────────────────────────

    @staticmethod
    def create_tables(conn) -> None:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volumes (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                volume_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                summary TEXT DEFAULT '',
                goal TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                is_locked INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_events (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                volume_id TEXT NOT NULL,
                event_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                summary TEXT DEFAULT '',
                goal TEXT DEFAULT '',
                status TEXT DEFAULT 'pending',
                is_locked INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (volume_id) REFERENCES volumes(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_templates (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                gender TEXT DEFAULT '',
                identity TEXT DEFAULT '',
                personality TEXT DEFAULT '',
                appearance TEXT DEFAULT '',
                background TEXT DEFAULT '',
                is_alive INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_states (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL UNIQUE,
                age TEXT DEFAULT '',
                location TEXT DEFAULT '',
                abilities TEXT DEFAULT '[]',
                inventory TEXT DEFAULT '[]',
                emotional_state TEXT DEFAULT '',
                custom_fields TEXT DEFAULT '{}',
                as_of_chapter INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (character_id) REFERENCES character_templates(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_relations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                character_a_id TEXT NOT NULL,
                character_b_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                strength INTEGER DEFAULT 5,
                description TEXT DEFAULT '',
                turning_point TEXT DEFAULT '',
                as_of_chapter INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (character_a_id) REFERENCES character_templates(id),
                FOREIGN KEY (character_b_id) REFERENCES character_templates(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cheat_systems (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                core_logic TEXT NOT NULL,
                limitations TEXT DEFAULT '',
                upgrade_conditions TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cheat_states (
                id TEXT PRIMARY KEY,
                cheat_id TEXT NOT NULL UNIQUE,
                current_level TEXT DEFAULT '',
                unlocked_features TEXT DEFAULT '[]',
                usage_status TEXT DEFAULT '{}',
                custom_fields TEXT DEFAULT '{}',
                as_of_chapter INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (cheat_id) REFERENCES cheat_systems(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_facts (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS foreshadowings (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                planted_chapter INTEGER NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'planted',
                collected_chapter INTEGER,
                collection_description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS open_threads (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                opened_chapter INTEGER NOT NULL,
                closed_chapter INTEGER,
                status TEXT DEFAULT 'open',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consistency_rules (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                target TEXT NOT NULL,
                condition TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()

    # ──────────────────────────────
    # Volume CRUD
    # ──────────────────────────────

    def list_volumes(self, project_id: str) -> List[Volume]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM volumes WHERE project_id = ? ORDER BY sort_order, volume_number",
                (project_id,),
            ).fetchall()
            return [self._row_to_volume(r) for r in rows]

    def get_volume(self, volume_id: str) -> Optional[Volume]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM volumes WHERE id = ?", (volume_id,)).fetchone()
            return self._row_to_volume(row) if row else None

    def create_volume(self, v: Volume):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO volumes (id,project_id,volume_number,title,summary,goal,
                   status,is_locked,sort_order,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (v.id, v.project_id, v.volume_number, v.title, v.summary, v.goal,
                 v.status.value, int(v.is_locked), v.sort_order,
                 v.created_at.isoformat(), v.updated_at.isoformat()),
            )
            conn.commit()

    def update_volume(self, v: Volume):
        v.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """UPDATE volumes SET title=?,summary=?,goal=?,status=?,is_locked=?,
                   sort_order=?,updated_at=? WHERE id=?""",
                (v.title, v.summary, v.goal, v.status.value, int(v.is_locked),
                 v.sort_order, v.updated_at.isoformat(), v.id),
            )
            conn.commit()

    # ──────────────────────────────
    # StoryEvent CRUD
    # ──────────────────────────────

    def list_events(self, project_id: str, volume_id: Optional[str] = None) -> List[StoryEvent]:
        with self._connection() as conn:
            sql = "SELECT * FROM story_events WHERE project_id = ?"
            params: list = [project_id]
            if volume_id:
                sql += " AND volume_id = ?"
                params.append(volume_id)
            sql += " ORDER BY sort_order, event_number"
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_event(r) for r in rows]

    def get_event(self, event_id: str) -> Optional[StoryEvent]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM story_events WHERE id = ?", (event_id,)).fetchone()
            return self._row_to_event(row) if row else None

    def create_event(self, e: StoryEvent):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO story_events (id,project_id,volume_id,event_number,title,
                   summary,goal,status,is_locked,sort_order,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (e.id, e.project_id, e.volume_id, e.event_number, e.title,
                 e.summary, e.goal, e.status.value, int(e.is_locked), e.sort_order,
                 e.created_at.isoformat(), e.updated_at.isoformat()),
            )
            conn.commit()

    def update_event(self, e: StoryEvent):
        e.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """UPDATE story_events SET title=?,summary=?,goal=?,status=?,
                   is_locked=?,sort_order=?,updated_at=? WHERE id=?""",
                (e.title, e.summary, e.goal, e.status.value, int(e.is_locked),
                 e.sort_order, e.updated_at.isoformat(), e.id),
            )
            conn.commit()

    # ──────────────────────────────
    # Character CRUD
    # ──────────────────────────────

    def list_characters(self, project_id: str) -> List[CharacterTemplate]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM character_templates WHERE project_id = ? ORDER BY name",
                (project_id,),
            ).fetchall()
            return [self._row_to_character(r) for r in rows]

    def get_character(self, char_id: str) -> Optional[CharacterTemplate]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM character_templates WHERE id = ?", (char_id,)).fetchone()
            return self._row_to_character(row) if row else None

    def create_character(self, c: CharacterTemplate):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO character_templates (id,project_id,name,gender,identity,
                   personality,appearance,background,is_alive,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (c.id, c.project_id, c.name, c.gender, c.identity, c.personality,
                 c.appearance, c.background, int(c.is_alive),
                 c.created_at.isoformat(), c.updated_at.isoformat()),
            )
            conn.commit()

    def update_character(self, c: CharacterTemplate):
        c.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """UPDATE character_templates SET name=?,gender=?,identity=?,personality=?,
                   appearance=?,background=?,is_alive=?,updated_at=? WHERE id=?""",
                (c.name, c.gender, c.identity, c.personality, c.appearance, c.background,
                 int(c.is_alive), c.updated_at.isoformat(), c.id),
            )
            conn.commit()

    def get_character_state(self, character_id: str) -> Optional[CharacterState]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM character_states WHERE character_id = ?", (character_id,)
            ).fetchone()
            return self._row_to_char_state(row) if row else None

    def upsert_character_state(self, s: CharacterState):
        s.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO character_states (id,character_id,age,location,abilities,
                   inventory,emotional_state,custom_fields,as_of_chapter,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(character_id) DO UPDATE SET
                   age=excluded.age, location=excluded.location,
                   abilities=excluded.abilities, inventory=excluded.inventory,
                   emotional_state=excluded.emotional_state,
                   custom_fields=excluded.custom_fields,
                   as_of_chapter=excluded.as_of_chapter,
                   updated_at=excluded.updated_at""",
                (s.id, s.character_id, s.age, s.location,
                 json.dumps(s.abilities, ensure_ascii=False),
                 json.dumps(s.inventory, ensure_ascii=False),
                 s.emotional_state,
                 json.dumps(s.custom_fields, ensure_ascii=False),
                 s.as_of_chapter, s.updated_at.isoformat()),
            )
            conn.commit()

    # ──────────────────────────────
    # Character Relations
    # ──────────────────────────────

    def list_relations(self, project_id: str) -> List[CharacterRelation]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM character_relations WHERE project_id = ? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
            return [self._row_to_relation(r) for r in rows]

    def create_relation(self, r: CharacterRelation):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO character_relations (id,project_id,character_a_id,character_b_id,
                   relation_type,strength,description,turning_point,as_of_chapter,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (r.id, r.project_id, r.character_a_id, r.character_b_id, r.relation_type,
                 r.strength, r.description, r.turning_point, r.as_of_chapter,
                 r.updated_at.isoformat()),
            )
            conn.commit()

    def update_relation(self, r: CharacterRelation):
        r.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """UPDATE character_relations SET relation_type=?,strength=?,description=?,
                   turning_point=?,as_of_chapter=?,updated_at=? WHERE id=?""",
                (r.relation_type, r.strength, r.description, r.turning_point,
                 r.as_of_chapter, r.updated_at.isoformat(), r.id),
            )
            conn.commit()

    # ──────────────────────────────
    # Cheat System
    # ──────────────────────────────

    def list_cheats(self, project_id: str) -> List[CheatSystem]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM cheat_systems WHERE project_id = ?", (project_id,)
            ).fetchall()
            return [self._row_to_cheat(r) for r in rows]

    def create_cheat(self, c: CheatSystem):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO cheat_systems (id,project_id,name,core_logic,limitations,
                   upgrade_conditions,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (c.id, c.project_id, c.name, c.core_logic, c.limitations,
                 c.upgrade_conditions, c.created_at.isoformat(), c.updated_at.isoformat()),
            )
            conn.commit()

    def get_cheat_state(self, cheat_id: str) -> Optional[CheatState]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM cheat_states WHERE cheat_id = ?", (cheat_id,)
            ).fetchone()
            return self._row_to_cheat_state(row) if row else None

    def upsert_cheat_state(self, s: CheatState):
        s.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO cheat_states (id,cheat_id,current_level,unlocked_features,
                   usage_status,custom_fields,as_of_chapter,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(cheat_id) DO UPDATE SET
                   current_level=excluded.current_level,
                   unlocked_features=excluded.unlocked_features,
                   usage_status=excluded.usage_status,
                   custom_fields=excluded.custom_fields,
                   as_of_chapter=excluded.as_of_chapter,
                   updated_at=excluded.updated_at""",
                (s.id, s.cheat_id, s.current_level,
                 json.dumps(s.unlocked_features, ensure_ascii=False),
                 json.dumps(s.usage_status, ensure_ascii=False),
                 json.dumps(s.custom_fields, ensure_ascii=False),
                 s.as_of_chapter, s.updated_at.isoformat()),
            )
            conn.commit()

    # ──────────────────────────────
    # World Facts
    # ──────────────────────────────

    def list_world_facts(self, project_id: str, category: Optional[str] = None) -> List[WorldFact]:
        with self._connection() as conn:
            sql = "SELECT * FROM world_facts WHERE project_id = ?"
            params: list = [project_id]
            if category:
                sql += " AND category = ?"
                params.append(category)
            sql += " ORDER BY category, title"
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_world_fact(r) for r in rows]

    def create_world_fact(self, f: WorldFact):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO world_facts (id,project_id,category,title,content,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (f.id, f.project_id, f.category, f.title, f.content,
                 f.created_at.isoformat(), f.updated_at.isoformat()),
            )
            conn.commit()

    def update_world_fact(self, f: WorldFact):
        f.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                "UPDATE world_facts SET category=?,title=?,content=?,updated_at=? WHERE id=?",
                (f.category, f.title, f.content, f.updated_at.isoformat(), f.id),
            )
            conn.commit()

    def delete_world_fact(self, fact_id: str):
        with self._connection() as conn:
            conn.execute("DELETE FROM world_facts WHERE id = ?", (fact_id,))
            conn.commit()

    # ──────────────────────────────
    # Foreshadowings
    # ──────────────────────────────

    def list_foreshadowings(self, project_id: str, status: Optional[str] = None) -> List[Foreshadowing]:
        with self._connection() as conn:
            sql = "SELECT * FROM foreshadowings WHERE project_id = ?"
            params: list = [project_id]
            if status:
                sql += " AND status = ?"
                params.append(status)
            sql += " ORDER BY planted_chapter"
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_foreshadowing(r) for r in rows]

    def create_foreshadowing(self, f: Foreshadowing):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO foreshadowings (id,project_id,planted_chapter,description,
                   status,collected_chapter,collection_description,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (f.id, f.project_id, f.planted_chapter, f.description, f.status.value,
                 f.collected_chapter, f.collection_description,
                 f.created_at.isoformat(), f.updated_at.isoformat()),
            )
            conn.commit()

    def update_foreshadowing(self, f: Foreshadowing):
        f.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """UPDATE foreshadowings SET status=?,collected_chapter=?,
                   collection_description=?,updated_at=? WHERE id=?""",
                (f.status.value, f.collected_chapter, f.collection_description,
                 f.updated_at.isoformat(), f.id),
            )
            conn.commit()

    # ──────────────────────────────
    # Open Threads
    # ──────────────────────────────

    def list_threads(self, project_id: str, status: Optional[str] = None) -> List[OpenThread]:
        with self._connection() as conn:
            sql = "SELECT * FROM open_threads WHERE project_id = ?"
            params: list = [project_id]
            if status:
                sql += " AND status = ?"
                params.append(status)
            sql += " ORDER BY priority DESC, opened_chapter"
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_thread(r) for r in rows]

    def create_thread(self, t: OpenThread):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO open_threads (id,project_id,title,description,priority,
                   opened_chapter,closed_chapter,status,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (t.id, t.project_id, t.title, t.description, t.priority.value,
                 t.opened_chapter, t.closed_chapter, t.status.value,
                 t.created_at.isoformat(), t.updated_at.isoformat()),
            )
            conn.commit()

    def update_thread(self, t: OpenThread):
        t.updated_at = datetime.now()
        with self._connection() as conn:
            conn.execute(
                """UPDATE open_threads SET title=?,description=?,priority=?,
                   closed_chapter=?,status=?,updated_at=? WHERE id=?""",
                (t.title, t.description, t.priority.value, t.closed_chapter,
                 t.status.value, t.updated_at.isoformat(), t.id),
            )
            conn.commit()

    # ──────────────────────────────
    # Consistency Rules
    # ──────────────────────────────

    def list_rules(self, project_id: str) -> List[ConsistencyRule]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM consistency_rules WHERE project_id = ? AND is_active = 1",
                (project_id,),
            ).fetchall()
            return [self._row_to_rule(r) for r in rows]

    def create_rule(self, r: ConsistencyRule):
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO consistency_rules (id,project_id,rule_type,target,
                   condition,is_active,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (r.id, r.project_id, r.rule_type, r.target, r.condition,
                 int(r.is_active), r.created_at.isoformat(), r.updated_at.isoformat()),
            )
            conn.commit()

    def toggle_rule(self, rule_id: str, is_active: bool):
        with self._connection() as conn:
            conn.execute(
                "UPDATE consistency_rules SET is_active=?, updated_at=? WHERE id=?",
                (int(is_active), datetime.now().isoformat(), rule_id),
            )
            conn.commit()

    # ──────────────────────────────
    # Row → Model 转换
    # ──────────────────────────────

    @staticmethod
    def _row_to_volume(r) -> Volume:
        from models import VolumeStatus
        return Volume(
            id=r["id"], project_id=r["project_id"], volume_number=r["volume_number"],
            title=r["title"], summary=r["summary"] or "", goal=r["goal"] or "",
            status=VolumeStatus(r["status"]), is_locked=bool(r["is_locked"]),
            sort_order=r["sort_order"],
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_event(r) -> StoryEvent:
        from models import EventStatus
        return StoryEvent(
            id=r["id"], project_id=r["project_id"], volume_id=r["volume_id"],
            event_number=r["event_number"], title=r["title"],
            summary=r["summary"] or "", goal=r["goal"] or "",
            status=EventStatus(r["status"]), is_locked=bool(r["is_locked"]),
            sort_order=r["sort_order"],
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_character(r) -> CharacterTemplate:
        return CharacterTemplate(
            id=r["id"], project_id=r["project_id"], name=r["name"],
            gender=r["gender"] or "", identity=r["identity"] or "",
            personality=r["personality"] or "", appearance=r["appearance"] or "",
            background=r["background"] or "", is_alive=bool(r["is_alive"]),
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_char_state(r) -> CharacterState:
        return CharacterState(
            id=r["id"], character_id=r["character_id"],
            age=r["age"] or "", location=r["location"] or "",
            abilities=json.loads(r["abilities"]) if r["abilities"] else [],
            inventory=json.loads(r["inventory"]) if r["inventory"] else [],
            emotional_state=r["emotional_state"] or "",
            custom_fields=json.loads(r["custom_fields"]) if r["custom_fields"] else {},
            as_of_chapter=r["as_of_chapter"] or 0,
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_relation(r) -> CharacterRelation:
        return CharacterRelation(
            id=r["id"], project_id=r["project_id"],
            character_a_id=r["character_a_id"], character_b_id=r["character_b_id"],
            relation_type=r["relation_type"], strength=r["strength"],
            description=r["description"] or "", turning_point=r["turning_point"] or "",
            as_of_chapter=r["as_of_chapter"] or 0,
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_cheat(r) -> CheatSystem:
        return CheatSystem(
            id=r["id"], project_id=r["project_id"], name=r["name"],
            core_logic=r["core_logic"], limitations=r["limitations"] or "",
            upgrade_conditions=r["upgrade_conditions"] or "",
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_cheat_state(r) -> CheatState:
        return CheatState(
            id=r["id"], cheat_id=r["cheat_id"],
            current_level=r["current_level"] or "",
            unlocked_features=json.loads(r["unlocked_features"]) if r["unlocked_features"] else [],
            usage_status=json.loads(r["usage_status"]) if r["usage_status"] else {},
            custom_fields=json.loads(r["custom_fields"]) if r["custom_fields"] else {},
            as_of_chapter=r["as_of_chapter"] or 0,
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_world_fact(r) -> WorldFact:
        return WorldFact(
            id=r["id"], project_id=r["project_id"], category=r["category"],
            title=r["title"], content=r["content"],
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_foreshadowing(r) -> Foreshadowing:
        from models import ForeshadowStatus
        return Foreshadowing(
            id=r["id"], project_id=r["project_id"],
            planted_chapter=r["planted_chapter"], description=r["description"],
            status=ForeshadowStatus(r["status"]),
            collected_chapter=r["collected_chapter"],
            collection_description=r["collection_description"] or "",
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_thread(r) -> OpenThread:
        from models import ThreadStatus, ThreadPriority
        return OpenThread(
            id=r["id"], project_id=r["project_id"], title=r["title"],
            description=r["description"],
            priority=ThreadPriority(r["priority"]),
            opened_chapter=r["opened_chapter"],
            closed_chapter=r["closed_chapter"],
            status=ThreadStatus(r["status"]),
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )

    @staticmethod
    def _row_to_rule(r) -> ConsistencyRule:
        return ConsistencyRule(
            id=r["id"], project_id=r["project_id"],
            rule_type=r["rule_type"], target=r["target"], condition=r["condition"],
            is_active=bool(r["is_active"]),
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )
