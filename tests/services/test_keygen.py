import hashlib

from keys.keygen import generate_key


def test_raw_key_has_expected_prefix():
    raw_key, _ = generate_key()
    assert raw_key.startswith("sk_live_")


def test_custom_prefix_is_respected():
    raw_key, _ = generate_key(prefix="sk_test")
    assert raw_key.startswith("sk_test_")


def test_key_hash_matches_sha256_of_raw_key():
    raw_key, key_hash = generate_key()
    assert key_hash == hashlib.sha256(raw_key.encode()).hexdigest()


def test_successive_keys_are_unique():
    """Regression guard: keys must never collide."""
    keys = {generate_key()[0] for _ in range(50)}
    assert len(keys) == 50
