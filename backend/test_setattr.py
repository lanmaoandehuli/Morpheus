# Test setattr on Pydantic model
from models import StoryEvent
from datetime import datetime

e = StoryEvent(
    id="test", project_id="p", volume_id="v",
    event_number=1, title="test",
    created_at=datetime.now(), updated_at=datetime.now()
)
print(f'Before: {e.involved_character_ids}')

# Direct setattr
e.involved_character_ids = ['x', 'y']
print(f'Direct: {e.involved_character_ids}')

# Using setattr
setattr(e, 'involved_character_ids', ['a', 'b'])
print(f'setattr: {e.involved_character_ids}')

print(f'model_dump: {e.model_dump()["involved_character_ids"]}')
