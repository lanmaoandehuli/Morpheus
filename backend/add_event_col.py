import sqlite3
db = r'D:\openclaw\.openclaw\Morpheus\data\projects\b8fa8f17-b057-48b1-accb-99c255c31115\novelist.db'
conn = sqlite3.connect(db)
existing = {r[1] for r in conn.execute('PRAGMA table_info(story_events)').fetchall()}
if 'involved_character_ids' not in existing:
    conn.execute("ALTER TABLE story_events ADD COLUMN involved_character_ids TEXT DEFAULT '[]'")
    print('Added involved_character_ids to story_events')
else:
    print('Column already exists')
conn.commit()
conn.close()
