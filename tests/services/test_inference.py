import numpy as np
import pandas as pd
import pytest
from fastapi import HTTPException

from services import inference


class _FakeModel:
    """Stand-in for a fitted sklearn/xgboost classifier."""

    feature_names_in_ = np.array(["amount", "hour"])

    def predict(self, X):
        return np.array([1 if a > 100 else 0 for a in X["amount"]])

    def predict_proba(self, X):
        return np.array([[0.1, 0.9] if a > 100 else [0.9, 0.1] for a in X["amount"]])


@pytest.fixture()
def fake_model(monkeypatch):
    model = _FakeModel()
    monkeypatch.setattr(inference, "load_model", lambda model_id: model)
    return model


def test_predict_returns_predictions_and_probabilities(fake_model):
    df = pd.DataFrame({"amount": [10, 200], "hour": [1, 2]})

    result = inference.predict("any-model-id", df)

    assert result["predictions"] == [0, 1]
    assert result["probabilities"] == [[0.9, 0.1], [0.1, 0.9]]


def test_predict_attaches_prediction_column_to_full_data(fake_model):
    df = pd.DataFrame({"amount": [10], "hour": [1]})

    result = inference.predict("any-model-id", df)

    assert result["full_data"][0]["prediction"] == 0
    assert result["full_data"][0]["amount"] == 10


def test_predict_raises_422_when_columns_dont_match_model(fake_model):
    df = pd.DataFrame({"amount": [10]})  # missing "hour"

    with pytest.raises(HTTPException) as exc_info:
        inference.predict("any-model-id", df)

    assert exc_info.value.status_code == 422
