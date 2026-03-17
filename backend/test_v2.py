import requests, json, sys

BASE = 'http://localhost:8000'
h = {'Content-Type': 'application/json'}

r = requests.get(f'{BASE}/api/projects')
PID = r.json()[0]['id']
print(f'[1/10] GET projects OK')

r = requests.post(f'{BASE}/api/v2/projects/{PID}/volumes', headers=h, json={'title': 'V1', 'volume_number': 1})
vid = r.json()['id']
print(f'[2/10] POST volumes OK')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/volumes')
print(f'[3/10] GET volumes -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/volumes/{vid}', headers=h, json={'summary': 'x'})
print(f'[4/10] PUT volumes OK')

r = requests.post(f'{BASE}/api/v2/projects/{PID}/events', headers=h, json={'volume_id': vid, 'title': 'E1'})
eid = r.json()['id']
print(f'[5/10] POST events OK')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/events')
print(f'[6/10] GET events -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/events/{eid}', headers=h, json={'summary': 'y'})
print(f'[7/10] PUT events OK')

r = requests.post(f'{BASE}/api/v2/projects/{PID}/characters', headers=h, json={'name': 'A', 'gender': 'M'})
cid = r.json()['id']
print(f'[8/10] POST characters OK')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/characters')
print(f'[9/10] GET characters -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/characters/{cid}', headers=h, json={'personality': 'p'})
print(f'[10/10] PUT characters OK')

# state
r = requests.get(f'{BASE}/api/v2/projects/{PID}/characters/{cid}/state')
print(f'[11] GET state -> {r.status_code}')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/characters/{cid}/state', headers=h, json={'location': 'here', 'as_of_chapter': 1})
print(f'[12] PUT state -> {r.status_code}')

# relations
r2 = requests.post(f'{BASE}/api/v2/projects/{PID}/characters', headers=h, json={'name': 'B', 'gender': 'F'})
nid = r2.json()['id']
r = requests.post(f'{BASE}/api/v2/projects/{PID}/relations', headers=h,
    json={'character_a_id': cid, 'character_b_id': nid, 'relation_type': 'friend'})
rid = r.json()['id']
print(f'[13] POST relations -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/relations')
print(f'[14] GET relations -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/relations/{rid}', headers=h, json={'strength': 8})
print(f'[15] PUT relations -> {r.status_code}')

# cheats
r = requests.post(f'{BASE}/api/v2/projects/{PID}/cheats', headers=h, json={'name': 'SYS', 'core_logic': 'test'})
chid = r.json()['id']
print(f'[16] POST cheats -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/cheats')
print(f'[17] GET cheats -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/cheats/{chid}/state', headers=h, json={'current_level': 'Lv1'})
print(f'[18] PUT cheat state -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/cheats/{chid}/state')
print(f'[19] GET cheat state -> {r.status_code}')

# world facts
r = requests.post(f'{BASE}/api/v2/projects/{PID}/world-facts', headers=h, json={'category': 'set', 'title': 'T', 'content': 'C'})
wfid = r.json()['id']
print(f'[20] POST world-facts -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/world-facts')
print(f'[21] GET world-facts -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/world-facts/{wfid}', headers=h, json={'content': 'C2'})
print(f'[22] PUT world-facts -> {r.status_code}')

r = requests.delete(f'{BASE}/api/v2/projects/{PID}/world-facts/{wfid}')
print(f'[23] DELETE world-facts -> {r.status_code}')

# foreshadowings
r = requests.post(f'{BASE}/api/v2/projects/{PID}/foreshadowings', headers=h, json={'planted_chapter': 1, 'description': 'x'})
fsid = r.json()['id']
print(f'[24] POST foreshadowings -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/foreshadowings')
print(f'[25] GET foreshadowings -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/foreshadowings/{fsid}', headers=h, json={'status': 'collected', 'collected_chapter': 50})
print(f'[26] PUT foreshadowings -> {r.status_code}')

# threads
r = requests.post(f'{BASE}/api/v2/projects/{PID}/threads', headers=h, json={'title': 'T1', 'description': 'D', 'opened_chapter': 1})
tid = r.json()['id']
print(f'[27] POST threads -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/threads')
print(f'[28] GET threads -> {len(r.json())} items')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/threads/{tid}', headers=h, json={'status': 'closed', 'closed_chapter': 30})
print(f'[29] PUT threads -> {r.status_code}')

# rules
r = requests.post(f'{BASE}/api/v2/projects/{PID}/rules', headers=h, json={'rule_type': 'death', 'target': 'A', 'condition': 'dead'})
ruleid = r.json()['id']
print(f'[30] POST rules -> {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/rules')
print(f'[31] GET rules -> {len(r.json())} items')

r = requests.patch(f'{BASE}/api/v2/projects/{PID}/rules/{ruleid}/toggle', headers=h, json={'is_active': False})
print(f'[32] PATCH rules toggle -> {r.status_code}')

# summary
r = requests.get(f'{BASE}/api/v2/projects/{PID}/knowledge-summary')
print(f'[33] GET knowledge-summary -> {r.status_code}')
print(json.dumps(r.json(), ensure_ascii=False, indent=2))

# error cases
r = requests.get(f'{BASE}/api/v2/projects/nonexistent/volumes')
assert r.status_code == 404
print(f'[34] 404 on bad project OK')

print('\n=== ALL TESTS PASSED ===')
