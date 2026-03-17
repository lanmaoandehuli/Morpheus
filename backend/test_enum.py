from models import StoryEvent
from datetime import datetime

def _enum_val(model_class, field_name, value):
    field_info = model_class.model_fields.get(field_name)
    print(f'  field_info={field_info}, annotation={field_info.annotation if field_info else None}')
    if field_info and hasattr(field_info.annotation, '__mro__'):
        for cls in field_info.annotation.__mro__:
            if cls.__name__ == 'Enum' or hasattr(cls, '_value2member_map_'):
                return cls(value)
    return value

test_val = ['aaa', 'bbb']
result = _enum_val(StoryEvent, 'involved_character_ids', test_val)
print(f'Result: {result}, type: {type(result)}')

e = StoryEvent(id="t", project_id="p", volume_id="v", event_number=1, title="t", created_at=datetime.now(), updated_at=datetime.now())
setattr(e, 'involved_character_ids', result)
print(f'e.involved_character_ids: {e.involved_character_ids}')
