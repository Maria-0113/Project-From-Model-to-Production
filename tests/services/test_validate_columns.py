import pandas as pd
import pytest
from fastapi import HTTPException

from services.validate_columns import validate_columns


def test_passes_when_columns_match_exactly():
    df = pd.DataFrame({"amount": [1], "hour": [2]})
    # Should not raise
    assert validate_columns(df, ["amount", "hour"]) is None


def test_passes_when_df_has_extra_columns():
    """Extra columns are allowed; only missing ones are an error."""
    df = pd.DataFrame({"amount": [1], "hour": [2], "extra": [3]})
    assert validate_columns(df, ["amount", "hour"]) is None


def test_raises_422_when_column_missing():
    df = pd.DataFrame({"amount": [1]})
    with pytest.raises(HTTPException) as exc_info:
        validate_columns(df, ["amount", "hour"])

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["missing_columns"] == ["hour"]


def test_error_detail_lists_extra_columns_too():
    df = pd.DataFrame({"amount": [1], "unexpected": [2]})
    with pytest.raises(HTTPException) as exc_info:
        validate_columns(df, ["amount", "hour"])

    detail = exc_info.value.detail
    assert detail["missing_columns"] == ["hour"]
    assert detail["extra_columns"] == ["unexpected"]


def test_accepts_numpy_str_expected_columns():
    """expected_columns can come from model.feature_names_in_ (numpy str_ objects)."""
    import numpy as np

    df = pd.DataFrame({"amount": [1]})
    expected = np.array(["amount"], dtype=object)
    assert validate_columns(df, expected) is None
