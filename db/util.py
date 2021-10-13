import random

id_chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def gen_id(k=8):
    return ''.join(random.choices(id_chars, k=6))