import requests, json
BASE = 'http://localhost:8000'
h = {'Content-Type': 'application/json'}

r = requests.get(f'{BASE}/api/projects')
PID = r.json()[0]['id']
print('server OK')

# threads - test PUT with status enum
r = requests.post(f'{BASE}/api/v2/projects/{PID}/threads', headers=h,
    json={'title': 'T', 'description': 'D', 'opened_chapter': 1})
tid = r.json()['id']
print(f'POST threads {r.status_code}')

r = requests.put(f'{BASE}/api/v2/projects/{PID}/threads/{tid}', headers=h,
    json={'status': 'closed', 'closed_chapter': 30})
print(f'PUT threads {r.status_code}')
if r.status_code != 200:
    print(f'  ERROR: {r.text[:300]}')

# rules
r = requests.post(f'{BASE}/api/v2/projects/{PID}/rules', headers=h,
    json={'rule_type': 'death', 'target': 'A', 'condition': 'dead'})
ruleid = r.json()['id']
print(f'POST rules {r.status_code}')

r = requests.get(f'{BASE}/api/v2/projects/{PID}/rules')
print(f'GET rules {r.status_code} {len(r.json())} items')

r = requests.patch(f'{BASE}/api/v2/projects/{PID}/rules/{ruleid}/toggle', headers=h,
    json={'is_active': False})
print(f'PATCH toggle {r.status_code}')

# summary
r = requests.get(f'{BASE}/api/v2/projects/{PID}/knowledge-summary')
print(f'GET summary {r.status_code}')
print(json.dumps(r.json(), ensure_ascii=False, indent=2))

# 404
r = requests.get(f'{BASE}/api/v2/projects/nonexistent/volumes')
print(f'404 test {r.status_code}')

print('ALL DONE')
