import io

import pytest
from fastapi import HTTPException

from services.validate_csv import validate_csv


class _FakeUploadFile:
    """Minimal stand-in for FastAPI's UploadFile (has a `.file` attribute)."""

    def __init__(self, content: bytes):
        self.file = io.BytesIO(content)


def test_valid_csv_path_returns_dataframe(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("amount,hour\n10,1\n20,2\n")

    df = validate_csv(str(csv_path))

    assert list(df.columns) == ["amount", "hour"]
    assert len(df) == 2


def test_valid_uploadfile_returns_dataframe():
    fake_file = _FakeUploadFile(b"amount,hour\n10,1\n")

    df = validate_csv(fake_file)

    assert list(df.columns) == ["amount", "hour"]
    assert len(df) == 1


def test_empty_csv_raises_400(tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("amount,hour\n")  # header only, no rows

    with pytest.raises(HTTPException) as exc_info:
        validate_csv(str(csv_path))

    assert exc_info.value.status_code == 400
    assert "no rows" in exc_info.value.detail


def test_malformed_file_raises_400(tmp_path):
    bad_path = tmp_path / "not_a_csv.bin"
    bad_path.write_bytes(b"\x00\x01\x02\x03garbage")

    with pytest.raises(HTTPException) as exc_info:
        validate_csv(str(bad_path))

    assert exc_info.value.status_code == 400


def test_nonexistent_path_raises_400():
    with pytest.raises(HTTPException) as exc_info:
        validate_csv("/no/such/file.csv")

    assert exc_info.value.status_code == 400
