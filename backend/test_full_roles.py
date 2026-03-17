import requests, sqlite3, glob
PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
BASE = f'http://localhost:8000/api/v2/projects/{PID}'
H = {'Content-Type': 'application/json'}

# Clean old characters
for c in requests.get(f'{BASE}/characters').json():
    requests.delete(f'{BASE}/characters/{c["id"]}')

# Create protagonist
r1 = requests.post(f'{BASE}/characters', headers=H, json={
    'name': '李逍遥', 'role_type': 'protagonist', 'gender': '男',
    'identity': '穿越者，现代大学生', 'personality': '乐观机智、重情重义'
})
print(f'Protagonist: {r1.status_code} role={r1.json().get("role_type")}')

# Create villain
r2 = requests.post(f'{BASE}/characters', headers=H, json={
    'name': '赵无极', 'role_type': 'villain', 'gender': '男',
    'identity': '武林盟主',
    'personality': '阴险狡诈、城府极深、表面仁义实则野心勃勃',
    'motivation': '统一武林、称霸天下'
})
print(f'Villain: {r2.status_code} role={r2.json().get("role_type")} motivation={r2.json().get("motivation","-")[:10]}')

# Create supporting
r3 = requests.post(f'{BASE}/characters', headers=H, json={
    'name': '苏婉儿', 'role_type': 'supporting', 'gender': '女',
    'identity': '药王谷传人', 'personality': '外冷内热、医者仁心'
})
print(f'Supporting: {r3.status_code}')

# Create minion
r4 = requests.post(f'{BASE}/characters', headers=H, json={
    'name': '黑衣人甲', 'role_type': 'minion', 'gender': '男',
    'identity': '赵无极手下'
})
print(f'Minion: {r4.status_code}')

# Add state for protagonist
cid1 = r1.json()['id']
requests.put(f'{BASE}/characters/{cid1}/state', headers=H, json={
    'age': '22', 'status': '修炼中', 'location': '新手村',
    'battle_power': '练气三层', 'weapons': ['无'],
    'abilities': ['基础剑法', '系统鉴宝']
})

# Add state for villain
cid2 = r2.json()['id']
requests.put(f'{BASE}/characters/{cid2}/state', headers=H, json={
    'age': '45', 'status': '健康', 'location': '武林盟总坛',
    'battle_power': '一品巅峰', 'weapons': ['镇岳剑', '玄冥掌'],
    'abilities': ['玄冥神功', '镇岳剑法']
})

# Verify list
chars = requests.get(f'{BASE}/characters').json()
print(f'\nTotal: {len(chars)}')
for c in chars:
    print(f'  {c["name"]}: {c.get("role_type")} | {c.get("personality","")[:15]}')
