import random
import re
import string

from .models import URLMap

VALID_CUSTOM_ID = re.compile(r'^[A-Za-z0-9]{1,16}$')


def get_unique_short_id(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        candidate = ''.join(random.choice(alphabet) for _ in range(length))
        if not URLMap.query.filter_by(short=candidate).first():
            return candidate


def is_valid_custom_id(custom_id: str) -> bool:
    return bool(VALID_CUSTOM_ID.match(custom_id))
