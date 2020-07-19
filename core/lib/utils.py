from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


def password_digest(password):
    digest = hashes.Hash(hashes.BLAKE2b(64), backend=default_backend())
    digest.update(password.encode('utf-8'))
    return digest.finalize().hex()
