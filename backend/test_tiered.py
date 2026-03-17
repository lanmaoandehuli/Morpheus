import requests
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
H = {'Content-Type': 'application/json'}

# Get existing character IDs
chars = requests.get(f'{BASE}/characters').json()
pid_map = {c['name']: c['id'] for c in chars}
print('Characters:', list(pid_map.keys()))

# Get event ID
events = requests.get(f'{BASE}/events').json()
evt = events[0]
print(f'Event: {evt["title"]} id={evt["id"]}')

# Update event with involved characters (protagonist + villain + minion)
involved = [pid_map.get('李逍遥'), pid_map.get('赵无极'), pid_map.get('黑衣人甲')]
involved = [x for x in involved if x]
r = requests.put(f'{BASE}/events/{evt["id"]}', headers=H, json={
    'involved_character_ids': involved
})
print(f'Update event: {r.status_code}')

# Test knowledge context output
from api.main import _build_knowledge_context
from memory import MemoryStore
store = MemoryStore(r'../data/projects/{PID}', r'../data/projects/{PID}/novelist.db')
ctx = _build_knowledge_context(store, PID, 1)
print(f'\n--- Knowledge Context ---\n{ctx}')
