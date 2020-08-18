import re

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from django.db import models

REGX_EMAIL = re.compile(r'^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')


def password_digest(password):
    digest = hashes.Hash(hashes.BLAKE2b(64), backend=default_backend())
    digest.update(password.encode('utf-8'))
    return digest.finalize().hex()


def email_validate(email):
    if email:
        return REGX_EMAIL.match(email) is not None
    return False


def model_row_as_dict(model):
    result = None
    if isinstance(model, models.Model):
        result = {}
        for f in model._meta.fields:
            value = getattr(model, f.name)
            if value is not None:
                result[f.name] = str(value)
            else:
                result[f.name] = value
    return result


def model_as_dict(qs):
    result = None
    if isinstance(qs, (models.QuerySet, list)):
        result = []
        for r in qs:
            result.append(model_row_as_dict(r))
    else:
        result = model_row_as_dict(qs)
    return result