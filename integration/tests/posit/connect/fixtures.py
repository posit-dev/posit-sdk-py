from __future__ import annotations

import random
import string


def name() -> str:
    """Generate a unique name."""
    return "".join(random.choices(string.ascii_letters, k=8))


def email() -> str:
    """Generate a unique email address."""
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}@example.com"


def username() -> str:
    """Generate a unique username."""
    return "".join(random.choices(string.ascii_letters, k=8))


def password() -> str:
    """Generate a secure password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choices(characters, k=12))  # 12-character password
