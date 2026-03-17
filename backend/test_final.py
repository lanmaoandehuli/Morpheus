import requests
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
H = {'Content-Type': 'application/json'}

# Get character IDs
chars = requests.get(f'{BASE}/characters').json()
pid_map = {c['name']: c['id'] for c in chars}

# Set event involved characters
r = requests.put(f'{BASE}/events/e5503d51-c7af-4575-8a8f-84e1cfeca872', headers=H, json={
    'title': '觉醒系统',
    'involved_character_ids': [pid_map['李逍遥'], pid_map['赵无极'], pid_map['黑衣人甲']]
})
print(f'Event updated: {r.status_code}')

# Now test knowledge context by triggering a draft gen check
# Direct import won't work due to hot reload, so let's just check via a simple API call
# Check the events response
events = requests.get(f'{BASE}/events').json()
print(f'\nEvent: {events[0]["title"]}')
print(f'Involved: {events[0]["involved_character_ids"]}')

# Map IDs to names
id_name = {v: k for k, v in pid_map.items()}
print(f'Involved names: {[id_name.get(x, x) for x in events[0]["involved_character_ids"]]}')
