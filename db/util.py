import random

id_chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def gen_id(k=8, resource=None):
    if resource:
        id = ''.join(random.choices(id_chars, k=6))
        while id in resource:
            id = ''.join(random.choices(id_chars, k=6))
        return id
    else:
        return ''.join(random.choices(id_chars, k=6))