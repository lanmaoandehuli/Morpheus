import requests
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
H = {'Content-Type': 'application/json'}

r = requests.post(f'{BASE}/characters', headers=H, json={
    'name': '赵无极', 'role_type': 'villain', 'identity': '武林盟主',
    'personality': '阴险狡诈、城府极深、表面仁义实则野心勃勃',
    'motivation': '统一武林、称霸天下', 'gender': '男'
})
print(f'Create villain: {r.status_code}')
cid = r.json()['id']

r2 = requests.put(f'{BASE}/characters/{cid}/state', headers=H, json={
    'age': '45', 'status': '健康', 'location': '武林盟总坛',
    'battle_power': '一品巅峰', 'weapons': ['镇岳剑', '玄冥掌'],
    'abilities': ['玄冥神功', '镇岳剑法']
})
print(f'Upsert state: {r2.status_code}')

r3 = requests.get(f'{BASE}/characters/{cid}')
c = r3.json()
print(f'Role: {c.get("role_type")}, Motivation: {c.get("motivation")}')
