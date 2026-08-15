import numpy as np
import pandas as pd
import pytest

from services.detect_drift import detect_drift, any_csv


def _make_df(values, class_values=None, seed=0):
    n = len(values)
    return pd.DataFrame(
        {
            "amount": values,
            "Class": class_values if class_values is not None else [0] * n,
        }
    )


class TestDetectDriftValidation:
    def test_raises_typeerror_when_reference_df_not_dataframe(self):
        with pytest.raises(TypeError):
            detect_drift("not a dataframe", pd.DataFrame({"Class": [0]}))

    def test_raises_typeerror_when_current_df_not_dataframe(self):
        with pytest.raises(TypeError):
            detect_drift(pd.DataFrame({"Class": [0]}), "not a dataframe")

    def test_raises_valueerror_when_class_missing_from_reference(self):
        ref = pd.DataFrame({"amount": [1, 2]})
        cur = pd.DataFrame({"amount": [1, 2], "Class": [0, 1]})
        with pytest.raises(ValueError, match="reference_df"):
            detect_drift(ref, cur)

    def test_raises_valueerror_when_class_missing_from_current(self):
        ref = pd.DataFrame({"amount": [1, 2], "Class": [0, 1]})
        cur = pd.DataFrame({"amount": [1, 2]})
        with pytest.raises(ValueError, match="current_df"):
            detect_drift(ref, cur)

    def test_raises_valueerror_when_columns_differ(self):
        ref = pd.DataFrame({"amount": [1, 2], "Class": [0, 1]})
        cur = pd.DataFrame({"other_col": [1, 2], "Class": [0, 1]})
        with pytest.raises(ValueError, match="same columns"):
            detect_drift(ref, cur)

    @pytest.mark.parametrize("bad_alpha", [0, 1, -0.1, 1.5])
    def test_raises_valueerror_for_invalid_alpha(self, bad_alpha):
        ref = pd.DataFrame({"amount": [1, 2], "Class": [0, 1]})
        cur = pd.DataFrame({"amount": [1, 2], "Class": [0, 1]})
        with pytest.raises(ValueError, match="alpha"):
            detect_drift(ref, cur, alpha=bad_alpha)


class TestDetectDriftBehavior:
    def test_identical_distributions_report_no_drift(self):
        rng = np.random.default_rng(42)
        values = rng.normal(loc=0, scale=1, size=200).tolist()
        ref = _make_df(values)
        cur = _make_df(values)  # exact same distribution

        report, is_drifted = detect_drift(ref, cur)

        assert is_drifted is False
        assert bool(report.loc[0, "Drift"]) is False

    def test_clearly_shifted_distribution_is_flagged_as_drift(self):
        rng = np.random.default_rng(42)
        ref_values = rng.normal(loc=0, scale=1, size=300).tolist()
        cur_values = rng.normal(loc=10, scale=1, size=300).tolist()  # big shift
        ref = _make_df(ref_values)
        cur = _make_df(cur_values)

        report, is_drifted = detect_drift(ref, cur)

        assert is_drifted is True
        assert bool(report.loc[0, "Drift"]) is True

    def test_class_column_excluded_from_drift_features(self):
        ref = _make_df([1, 2, 3], class_values=[0, 1, 0])
        cur = _make_df([1, 2, 3], class_values=[1, 1, 1])  # Class differs a lot

        report, _ = detect_drift(ref, cur)

        assert "Class" not in report["Feature"].values

    def test_report_has_one_row_per_feature(self):
        ref = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "Class": [0, 1, 0]})
        cur = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "Class": [0, 1, 0]})

        report, _ = detect_drift(ref, cur)

        assert sorted(report["Feature"].tolist()) == ["a", "b"]


class TestAnyCsv:
    def test_reads_single_csv_file(self, tmp_path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("a,b\n1,2\n")

        df = any_csv(str(tmp_path))

        assert list(df.columns) == ["a", "b"]

    def test_returns_none_for_empty_production_folder(self):
        """any_csv special-cases the literal path 'src/data/production':
        if it has no CSVs (or doesn't exist), it returns None instead of
        raising, since 'no new production data yet' is an expected state."""
        result = any_csv("src/data/production")
        assert result is None

    def test_raises_when_multiple_csvs_present(self, tmp_path):
        (tmp_path / "a.csv").write_text("a\n1\n")
        (tmp_path / "b.csv").write_text("a\n1\n")

        with pytest.raises(ValueError, match="Expected exactly one"):
            any_csv(str(tmp_path))
