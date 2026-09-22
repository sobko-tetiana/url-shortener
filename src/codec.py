from ff3 import FF3Cipher

WIDTH = 12


def encrypt_id(key: str, tweak: str, id_value: int) -> str:
    padded = str(id_value).zfill(WIDTH)
    return FF3Cipher(key, tweak).encrypt(padded)


def decrypt_id(key: str, tweak: str, ciphertext: str) -> int:
    padded = FF3Cipher(key, tweak).decrypt(ciphertext)
    return int(padded)
