import requests
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
H = {'Content-Type': 'application/json'}

# Try with title too to see if ANY field updates
r = requests.put(f'{BASE}/events/e5503d51-c7af-4575-8a8f-84e1cfeca872', headers=H, json={
    'title': '觉醒系统X',
    'involved_character_ids': ['aaa', 'bbb']
})
print(f'Status: {r.status_code}')
data = r.json()
print(f'title: {data.get("title")}')
print(f'involved: {data.get("involved_character_ids")}')
