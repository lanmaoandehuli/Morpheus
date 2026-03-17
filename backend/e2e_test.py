import requests, json
PID = "b8fa8f17-b057-48b1-accb-99c255c31115"
BASE = f"http://localhost:8000/api/v2/projects/{PID}"
H = {"Content-Type": "application/json"}

# Create character
r = requests.post(f"{BASE}/characters", headers=H, json={"name": "李逍遥", "identity": "穿越者，现代大学生", "personality": "乐观机智", "is_alive": True})
print(f"Character: {r.status_code} {r.json()}")

# Get volume & event
vols = requests.get(f"{BASE}/volumes").json()
evts = requests.get(f"{BASE}/events").json()
vid, eid = vols[0]["id"], evts[0]["id"]
print(f"Volume: {vid}, Event: {eid}")

# Create chapter via v1 API
ch = requests.post(f"http://localhost:8000/api/projects/{PID}/chapters", headers=H,
    json={"project_id": PID, "chapter_number": 1, "title": "第一章 穿越", "goal": "主角穿越到宋朝，意外觉醒系统", "event_id": eid, "volume_id": vid})
print(f"Chapter: {ch.status_code} {ch.json()}")
