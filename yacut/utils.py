import random
import string

from .models import URLMap


def get_unique_short_id(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        candidate = ''.join(random.choice(alphabet) for _ in range(length))
        if not URLMap.query.filter_by(short=candidate).first():
            return candidate