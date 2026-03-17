import sys, os
sys.path.insert(0, r'D:\openclaw\.openclaw\Morpheus\backend')
os.chdir(r'D:\openclaw\.openclaw\Morpheus\backend')

PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
from api.main import _build_knowledge_context
from memory import MemoryStore
store = MemoryStore(f'../data/projects/{PID}', f'../data/projects/{PID}/novelist.db')
ctx = _build_knowledge_context(store, PID, 1)
print(ctx)
