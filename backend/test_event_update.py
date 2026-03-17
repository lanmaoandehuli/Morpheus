import requests
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
H = {'Content-Type': 'application/json'}

# Get characters
chars = requests.get(f'{BASE}/characters').json()
pid_map = {c['name']: c['id'] for c in chars}

# Get events
events = requests.get(f'{BASE}/events').json()
evt = events[0]
print(f'Before: involved={evt.get("involved_character_ids")}')

involved = [pid_map['李逍遥'], pid_map['赵无极'], pid_map['黑衣人甲']]
r = requests.put(f'{BASE}/events/{evt["id"]}', headers=H, json={
    'involved_character_ids': involved
})
print(f'PUT status: {r.status_code}')
print(f'Response: {r.json().get("involved_character_ids")}')

# Re-read
events2 = requests.get(f'{BASE}/events').json()
evt2 = events2[0]
print(f'After re-read: involved={evt2.get("involved_character_ids")}')
