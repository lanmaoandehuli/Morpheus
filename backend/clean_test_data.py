import requests
BASE = 'http://localhost:8000'
h = {'Content-Type': 'application/json'}

r = requests.get(f'{BASE}/api/projects')
PID = r.json()[0]['id']

# Delete world facts
for f in requests.get(f'{BASE}/api/v2/projects/{PID}/world-facts').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/world-facts/{f["id"]}')

# Delete volumes (cascade - events are orphaned but harmless)
for v in requests.get(f'{BASE}/api/v2/projects/{PID}/volumes').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/volumes/{v["id"]}')

# Delete events
for e in requests.get(f'{BASE}/api/v2/projects/{PID}/events').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/events/{e["id"]}')

# Delete characters
for c in requests.get(f'{BASE}/api/v2/projects/{PID}/characters').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/characters/{c["id"]}')

# Delete relations
for r2 in requests.get(f'{BASE}/api/v2/projects/{PID}/relations').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/relations/{r2["id"]}')

# Delete cheats
for c in requests.get(f'{BASE}/api/v2/projects/{PID}/cheats').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/cheats/{c["id"]}')

# Delete foreshadowings
for f in requests.get(f'{BASE}/api/v2/projects/{PID}/foreshadowings').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/foreshadowings/{f["id"]}')

# Delete threads
for t in requests.get(f'{BASE}/api/v2/projects/{PID}/threads').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/threads/{t["id"]}')

# Delete rules
for r2 in requests.get(f'{BASE}/api/v2/projects/{PID}/rules').json():
    requests.delete(f'{BASE}/api/v2/projects/{PID}/rules/{r2["id"]}')

# Verify
s = requests.get(f'{BASE}/api/v2/projects/{PID}/knowledge-summary').json()
print(f'Cleaned: {s}')
