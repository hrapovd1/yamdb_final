import random
import string


def get_random_string(length=12) -> str:
    return ''.join(
        random.choice(string.ascii_letters) for i in range(length)
    )
