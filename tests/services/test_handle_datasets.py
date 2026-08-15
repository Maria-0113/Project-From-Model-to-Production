import pytest

from services import handle_datasets


@pytest.fixture()
def data_dirs(tmp_path, monkeypatch):
    """Run move_data inside an isolated tmp 'data/' directory tree."""
    monkeypatch.chdir(tmp_path)
    incoming = tmp_path / "data" / "incoming"
    incoming.mkdir(parents=True)
    return {
        "incoming": incoming,
        "production": tmp_path / "data" / "production",
        "archive": tmp_path / "data" / "archive",
    }


def test_no_drift_moves_incoming_files_to_archive(data_dirs):
    (data_dirs["incoming"] / "new.csv").write_text("a,b\n1,2\n")

    handle_datasets.move_data(is_drift=False)

    archived = list(data_dirs["archive"].glob("*.csv"))
    assert len(archived) == 1
    assert not (data_dirs["incoming"] / "new.csv").exists()


def test_drift_moves_incoming_files_to_production(data_dirs):
    (data_dirs["incoming"] / "new.csv").write_text("a,b\n1,2\n")

    handle_datasets.move_data(is_drift=True)

    production_files = list(data_dirs["production"].glob("*.csv"))
    assert len(production_files) == 1


def test_drift_archives_existing_production_files_first(data_dirs):
    data_dirs["production"].mkdir(parents=True)
    old_file = data_dirs["production"] / "old_production.csv"
    old_file.write_text("a,b\n1,2\n")
    (data_dirs["incoming"] / "new.csv").write_text("a,b\n3,4\n")

    handle_datasets.move_data(is_drift=True)

    # old production file should now be archived
    assert (data_dirs["archive"] / "old_production.csv").exists()
    assert not old_file.exists()
    # new incoming file should now be in production
    assert len(list(data_dirs["production"].glob("*.csv"))) == 1


def test_no_incoming_files_is_a_noop(data_dirs):
    """Should not raise even if there's nothing to move."""
    handle_datasets.move_data(is_drift=False)
    assert list(data_dirs["archive"].glob("*.csv")) == []
