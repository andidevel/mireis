import re

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

REGX_EMAIL = re.compile(r'^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')


def password_digest(password):
    digest = hashes.Hash(hashes.BLAKE2b(64), backend=default_backend())
    digest.update(password.encode('utf-8'))
    return digest.finalize().hex()


def email_validate(email):
    if email:
        return REGX_EMAIL.match(email) is not None
    return False

