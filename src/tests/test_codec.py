import pytest

from src.codec import decode_base62, decrypt_id, encode_base62, encrypt_id
from src.settings import get_settings

settings = get_settings()


@pytest.mark.parametrize("value", ["0", "1", "62", "9999999999"])
def test_base62_roundtrip(value):
    assert decode_base62(encode_base62(value)) == value.zfill(10)


@pytest.mark.parametrize("id_value", [1, 42, 123456789])
def test_encrypt_decrypt_id_roundtrip(id_value):
    obfuscated_id = encrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, id_value
    )
    assert decrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, obfuscated_id
    ) == id_value


def test_id_survives_full_encode_pipeline():
    original_id = 555
    obfuscated_id = encrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, original_id
    )
    code = encode_base62(obfuscated_id)

    recovered_id = decrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, decode_base62(code)
    )

    assert recovered_id == original_id
