from pathlib import Path
import pandas as pd
import numpy as np
from .handle_datasets import move_data

from scipy.stats import ks_2samp


def detect_drift(reference_df, current_df, alpha=0.05, mean_threshold=0.2, std_threshold=0.2):

    """
    Compare the reference dataset
    with a new dataset

    Parameters
    ----------
    reference_df : pandas.DataFrame
        Original training data

    current_df : pandas.DataFrame
        New dataset

    alpha : float
        Significance level for KS test

    Returns
    -------
    pandas.DataFrame
        Drift report
    bool
        True if drift is detected, False otherwise
    """
    ###validation checks
    if not isinstance(reference_df, pd.DataFrame):
        raise TypeError("reference_df must be a pandas DataFrame")

    if not isinstance(current_df, pd.DataFrame):
        raise TypeError("current_df must be a pandas DataFrame")

    # Check target column exists
    if "Class" not in reference_df.columns:
        raise ValueError("'Class' column missing from reference_df")

    if "Class" not in current_df.columns:
        raise ValueError("'Class' column missing from current_df")

    # Check both datasets have the same features
    if set(reference_df.columns) != set(current_df.columns):
        raise ValueError("Datasets must contain the same columns")

    # Check alpha
    if not (0 < alpha < 1):
        raise ValueError("alpha must be between 0 and 1")
    
    ########


    results = []

    # Ignore the target column
    features = [c for c in reference_df.columns if c != "Class"]

    for feature in features:

        ref = reference_df[feature]
        cur = current_df[feature]

        # -------------------------
        # KS Test
        # -------------------------

        ks_statistic, p_value = ks_2samp(ref, cur)

        # -------------------------
        # Drift decision
        # -------------------------

        drift = (
            p_value < alpha
            and ks_statistic >= 0.02
        )

        results.append({

            "Feature": feature,

            "KS Statistic": round(ks_statistic, 4),
            "P-value": round(p_value, 6),

            "Drift": drift

        })
    is_drifted = any([r["Drift"] for r in results])
    return pd.DataFrame(results), is_drifted

def any_csv(path: str):
    incoming = Path(path)
    csv_files = list(incoming.glob("*.csv"))
    if path == "src/data/production" and len(csv_files) == 0:
        return None

    if len(csv_files) != 1:
        raise ValueError(
            f"Expected exactly one CSV file in {incoming}, found {len(csv_files)}."
        )
    return pd.read_csv(csv_files[0])
