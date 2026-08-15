import pytest
from fastapi import HTTPException

from services.model_exists import model_exists


def test_returns_model_when_it_exists(db_session, make_model_metadata):
    make_model_metadata(model_id="abc-123")

    result = model_exists("abc-123", db_session)

    assert result.id == "abc-123"


def test_raises_404_when_model_missing(db_session):
    with pytest.raises(HTTPException) as exc_info:
        model_exists("does-not-exist", db_session)

    assert exc_info.value.status_code == 404


def test_only_returns_the_requested_model(db_session, make_model_metadata):
    make_model_metadata(model_id="model-a")
    make_model_metadata(model_id="model-b")

    result = model_exists("model-b", db_session)

    assert result.id == "model-b"
