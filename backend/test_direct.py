# Direct test - bypass API
from memory import MemoryStore
from models import StoryEvent
import json

PID = 'b8fa8f17-b057-48b1-accb-99c255c31115'
store = MemoryStore(f'../data/projects/{PID}', f'../data/projects/{PID}/novelist.db')

e = store.knowledge.get_event('e5503d51-c7af-4575-8a8f-84e1cfeca872')
print(f'Before: {e.involved_character_ids}')

e.involved_character_ids = ['test1', 'test2']
print(f'After setattr: {e.involved_character_ids}')
store.knowledge.update_event(e)

e2 = store.knowledge.get_event('e5503d51-c7af-4575-8a8f-84e1cfeca872')
print(f'After save: {e2.involved_character_ids}')
