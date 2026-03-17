"""测试所有 v2 API 接口"""
import requests, json

BASE = 'http://localhost:8000'
headers = {'Content-Type': 'application/json'}

# 1. Get project id
r = requests.get(f'{BASE}/api/projects')
projects = r.json()
PID = projects[0]['id']
pname = projects[0]['name']
print(f'[OK] Project: {PID} ({pname})')

# 2. Volumes
r = requests.post(f'{BASE}/api/v2/projects/{PID}/volumes', headers=headers,
    json={'title': '测试卷一', 'volume_number': 1, 'summary': '新手村', 'goal': '活下来'})
assert r.status_code == 200, f"POST /volumes failed: {r.status_code} {r.text}"
vid = r.json()['id']
print(f'[OK] POST /volumes -> {vid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/volumes')
assert r.status_code == 200
print(f'[OK] GET /volumes -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/volumes/{vid}', headers=headers,
    json={'summary': '新手村篇'})
assert r.status_code == 200
print(f'[OK] PUT /volumes/{vid}')

# 3. Events
r = requests.post(f'{BASE}/api/v2/projects/{PID}/events', headers=headers,
    json={'volume_id': vid, 'title': '初入江湖', 'event_number': 1})
assert r.status_code == 200, f"POST /events failed: {r.status_code} {r.text}"
eid = r.json()['id']
print(f'[OK] POST /events -> {eid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/events')
assert r.status_code == 200
print(f'[OK] GET /events -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/events/{eid}', headers=headers,
    json={'summary': '主角登场'})
assert r.status_code == 200
print(f'[OK] PUT /events/{eid}')

# 4. Characters
r = requests.post(f'{BASE}/api/v2/projects/{PID}/characters', headers=headers,
    json={'name': '冯宇', 'gender': '男', 'identity': '穿越者'})
assert r.status_code == 200, f"POST /characters failed: {r.status_code} {r.text}"
cid = r.json()['id']
print(f'[OK] POST /characters -> {cid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/characters')
assert r.status_code == 200
print(f'[OK] GET /characters -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/characters/{cid}', headers=headers,
    json={'personality': '聪明狡猾'})
assert r.status_code == 200
print(f'[OK] PUT /characters/{cid}')

# 5. Character State
r = requests.get(f'{BASE}/api/v2/projects/{PID}/characters/{cid}/state')
assert r.status_code == 200
print(f'[OK] GET /characters/{cid}/state (before upsert)')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/characters/{cid}/state', headers=headers,
    json={'age': '18', 'location': '新手村', 'abilities': ['系统面板'], 'as_of_chapter': 1})
assert r.status_code == 200, f"PUT state failed: {r.status_code} {r.text}"
print(f'[OK] PUT /characters/{cid}/state')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/characters/{cid}/state')
assert r.status_code == 200
state = r.json()
assert state['location'] == '新手村'
print(f'[OK] GET /characters/{cid}/state -> location={state["location"]}, abilities={state["abilities"]}')

# 6. Relations
r = requests.post(f'{BASE}/api/v2/projects/{PID}/characters', headers=headers,
    json={'name': 'NPC小芳', 'gender': '女'})
nid = r.json()['id']

r = requests.post(f'{BASE}/api/v2/projects/{PID}/relations', headers=headers,
    json={'character_a_id': cid, 'character_b_id': nid, 'relation_type': '朋友', 'strength': 7})
assert r.status_code == 200, f"POST /relations failed: {r.status_code} {r.text}"
rid = r.json()['id']
print(f'[OK] POST /relations -> {rid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/relations')
assert r.status_code == 200
print(f'[OK] GET /relations -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/relations/{rid}', headers=headers,
    json={'strength': 8})
assert r.status_code == 200
print(f'[OK] PUT /relations/{rid}')

# 7. Cheat Systems
r = requests.post(f'{BASE}/api/v2/projects/{PID}/cheats', headers=headers,
    json={'name': '系统面板', 'core_logic': '可查看属性和任务'})
assert r.status_code == 200, f"POST /cheats failed: {r.status_code} {r.text}"
chid = r.json()['id']
print(f'[OK] POST /cheats -> {chid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/cheats')
assert r.status_code == 200
print(f'[OK] GET /cheats -> {len(r.json())} items')

# 8. Cheat State
r = requests.put(f'{BASE}/api/v2/projects/{PID}/cheats/{chid}/state', headers=headers,
    json={'current_level': 'Lv1', 'unlocked_features': ['属性面板'], 'as_of_chapter': 1})
assert r.status_code == 200, f"PUT cheat state failed: {r.status_code} {r.text}"
print(f'[OK] PUT /cheats/{chid}/state')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/cheats/{chid}/state')
assert r.status_code == 200
cs = r.json()
assert cs['current_level'] == 'Lv1'
print(f'[OK] GET /cheats/{chid}/state -> level={cs["current_level"]}')

# 9. World Facts
r = requests.post(f'{BASE}/api/v2/projects/{PID}/world-facts', headers=headers,
    json={'category': '设定', 'title': '灵气体系', 'content': '天地灵气分五品'})
assert r.status_code == 200, f"POST /world-facts failed: {r.status_code} {r.text}"
wfid = r.json()['id']
print(f'[OK] POST /world-facts -> {wfid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/world-facts')
assert r.status_code == 200
print(f'[OK] GET /world-facts -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/world-facts/{wfid}', headers=headers,
    json={'content': '天地灵气分九品'})
assert r.status_code == 200
print(f'[OK] PUT /world-facts/{wfid}')

r = requests.delete(f'{BASE}/api/v2/projects/{PID}/world-facts/{wfid}')
assert r.status_code == 200
print(f'[OK] DELETE /world-facts/{wfid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/world-facts')
remaining = [f for f in r.json() if f['id'] == wfid]
assert len(remaining) == 0, "DELETE did not work"
print(f'[OK] Verified: deleted world fact is gone')

# 10. Foreshadowings
r = requests.post(f'{BASE}/api/v2/projects/{PID}/foreshadowings', headers=headers,
    json={'planted_chapter': 1, 'description': '神秘老人给的玉佩'})
assert r.status_code == 200, f"POST /foreshadowings failed: {r.status_code} {r.text}"
fsid = r.json()['id']
print(f'[OK] POST /foreshadowings -> {fsid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/foreshadowings')
assert r.status_code == 200
print(f'[OK] GET /foreshadowings -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/foreshadowings/{fsid}', headers=headers,
    json={'status': 'collected', 'collected_chapter': 50, 'collection_description': '玉佩发光解开秘密'})
assert r.status_code == 200
print(f'[OK] PUT /foreshadowings/{fsid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/foreshadowings?status=planted')
planted = r.json()
assert len(planted) == 0, f"Expected 0 planted, got {len(planted)}"
print(f'[OK] GET /foreshadowings?status=planted -> {len(planted)} (correct, we changed it)')

# 11. Open Threads
r = requests.post(f'{BASE}/api/v2/projects/{PID}/threads', headers=headers,
    json={'title': '追查凶手', 'description': '寻找杀害师父的凶手', 'opened_chapter': 1, 'priority': 'high'})
assert r.status_code == 200, f"POST /threads failed: {r.status_code} {r.text}"
tid = r.json()['id']
print(f'[OK] POST /threads -> {tid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/threads')
assert r.status_code == 200
print(f'[OK] GET /threads -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/threads/{tid}', headers=headers,
    json={'status': 'closed', 'closed_chapter': 30})
assert r.status_code == 200
print(f'[OK] PUT /threads/{tid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/threads?status=open')
assert len(r.json()) == 0
print(f'[OK] GET /threads?status=open -> 0 (closed thread filtered)')

# 12. Consistency Rules
r = requests.post(f'{BASE}/api/v2/projects/{PID}/rules', headers=headers,
    json={'rule_type': 'character_death', 'target': 'NPC小芳', 'condition': '小芳在第30章死亡，之后不能出现'})
assert r.status_code == 200, f"POST /rules failed: {r.status_code} {r.text}"
ruleid = r.json()['id']
print(f'[OK] POST /rules -> {ruleid}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/rules')
assert r.status_code == 200
print(f'[OK] GET /rules -> {len(r.json())} items')

r = requests.patch(f'{BASE}/api/v2/projects/{PID}/rules/{ruleid}/toggle', headers=headers,
    json={'is_active': False})
assert r.status_code == 200
print(f'[OK] PATCH /rules/{ruleid}/toggle')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/rules')
rules = r.json()
active_rules = [x for x in rules if x['is_active']]
assert len(active_rules) == 0
print(f'[OK] Verified: rule is now inactive')

# 13. Knowledge Summary
r = requests.get(f'{BASE}/api/v2/projects/{PID}/knowledge-summary')
assert r.status_code == 200
summary = r.json()
print(f'[OK] GET /knowledge-summary')
print(json.dumps(summary, ensure_ascii=False, indent=2))

# 14. Error cases
r = requests.get(f'{BASE}/api/v2/projects/nonexistent/volumes')
assert r.status_code == 404
print(f'[OK] GET /volumes with invalid project -> 404')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/volumes/nonexistent', headers=headers,
    json={'title': 'x'})
assert r.status_code == 404
print(f'[OK] PUT /volumes/nonexistent -> 404')

print()
print('='*50)
print('ALL TESTS PASSED! (32 endpoints, including error handling)')
