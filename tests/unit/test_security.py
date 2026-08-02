from auth.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("Patient@12345")
    assert verify_password("Patient@12345", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    token = create_access_token("1", ["patient"])
    payload = decode_token(token)
    assert payload["sub"] == "1"
    assert payload["roles"] == ["patient"]
    assert payload["type"] == "access"
