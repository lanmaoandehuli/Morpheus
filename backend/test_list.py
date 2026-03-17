import requests
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
chars = requests.get(f'{BASE}/characters').json()
for c in chars:
    print(f'{c["name"]}: role={c.get("role_type")}, motivation={c.get("motivation","-")}, personality={c.get("personality","-")[:20]}')
