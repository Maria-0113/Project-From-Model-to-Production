import joblib
import pytest

from services.load_model import load_model


@pytest.fixture(autouse=True)
def _clear_cache():
    """load_model is @lru_cache'd, which would leak state between tests."""
    load_model.cache_clear()
    yield
    load_model.cache_clear()


def test_loads_model_from_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "models").mkdir()
    joblib.dump({"fake": "model"}, tmp_path / "models" / "abc.joblib")

    result = load_model("abc")

    assert result == {"fake": "model"}


def test_missing_model_raises_valueerror(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "models").mkdir()

    with pytest.raises(ValueError, match="not found on disk"):
        load_model("does-not-exist")


def test_second_call_uses_cache_not_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "models").mkdir()
    joblib.dump({"v": 1}, tmp_path / "models" / "cached.joblib")

    first = load_model("cached")
    # Overwrite the file on disk; a cached call should NOT see this change.
    joblib.dump({"v": 2}, tmp_path / "models" / "cached.joblib")
    second = load_model("cached")

    assert first is second
    assert second == {"v": 1}
