from ff3 import FF3Cipher

WIDTH = 10
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = 62


def encrypt_id(key: str, tweak: str, id_value: int) -> str:
    padded = str(id_value).zfill(WIDTH)
    return FF3Cipher(key, tweak).encrypt(padded)


def decrypt_id(key: str, tweak: str, ciphertext: str) -> int:
    padded = FF3Cipher(key, tweak).decrypt(ciphertext)
    return int(padded)


def encode_base62(value: str) -> str:
    num = int(value)
    if num == 0:
        return BASE62_ALPHABET[0]

    digits = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        digits.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(digits))


def decode_base62(code: str) -> str:
    num = 0
    for char in code:
        num = num * BASE + BASE62_ALPHABET.index(char)
    return str(num).zfill(WIDTH)
