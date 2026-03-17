import sqlite3
db = r'D:\openclaw\.openclaw\Morpheus\data\projects\b8fa8f17-b057-48b1-accb-99c255c31115\novelist.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT id, title, involved_character_ids FROM story_events').fetchall()
for r in rows:
    print(f'{r["title"]}: involved={r["involved_character_ids"]}')
conn.close()
