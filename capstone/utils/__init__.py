import random
import string


def get_random_string(
    length: int = 12,
    allowed_chars: str = string.ascii_letters+string.digits
) -> str:
    return "".join([random.choice(allowed_chars) for _ in range(length)])
