import sqlite3, json
db = r'D:\openclaw\.openclaw\Morpheus\data\projects\b8fa8f17-b057-48b1-accb-99c255c31115\novelist.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Check character role_types
rows = conn.execute('SELECT id, name, role_type, is_alive FROM character_templates').fetchall()
print('=== Characters ===')
for r in rows:
    print(f'  {r["name"]}: role_type={r["role_type"]}, alive={r["is_alive"]}')

# Check event involved_character_ids
rows = conn.execute('SELECT id, title, involved_character_ids FROM story_events').fetchall()
print('\n=== Events ===')
for r in rows:
    print(f'  {r["title"]}: involved={r["involved_character_ids"]}')

conn.close()
