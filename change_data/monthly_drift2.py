import numpy as np
import pandas as pd

def create_monthly_drift(df, month):

    drift = df.copy()

    fraud = drift["Class"] == 1
    n_fraud = fraud.sum()

    # 1. Gradual fraud-pattern drift


    v10_shift = 0.25 * month
    v14_shift = 0.20 * month

    drift.loc[fraud, "V10"] += np.random.normal(
        v10_shift,
        0.35,
        n_fraud
    )

    drift.loc[fraud, "V14"] -= np.random.normal(
        v14_shift,
        0.25,
        n_fraud
    )

    # 2. New fraud strategy

    strategy_probability = min(0.08 * month, 0.7)

    strategy_mask = fraud & (
        np.random.random(len(drift)) < strategy_probability
    )

    n_strategy = strategy_mask.sum()

    if n_strategy > 0:

        drift.loc[strategy_mask, "V12"] += np.random.normal(
            0.8,
            0.25,
            n_strategy
        )

    # 3. Second strategy appears later


    if month >= 6:

        strategy_probability = min(
            0.07 * (month - 5),
            0.5
        )

        strategy_mask = fraud & (
            np.random.random(len(drift)) < strategy_probability
        )

        n_strategy = strategy_mask.sum()

        if n_strategy > 0:

            drift.loc[strategy_mask, "V17"] -= np.random.normal(
                0.9,
                0.25,
                n_strategy
            )


    # 4. Amount behavior changes

    amount_probability = min(0.06 * month, 0.7)

    amount_mask = fraud & (
        np.random.random(len(drift)) < amount_probability
    )

    drift.loc[amount_mask, "Amount"] *= np.random.uniform(
        0.45,
        0.8,
        amount_mask.sum()
    )


    # 5. Population-wide Amount drift
    

    # Small but cumulative change affecting ALL transactions.
    # This makes PSI / KS much more likely to detect the drift.

    amount_factor = 1 + 0.015 * month

    drift["Amount"] *= np.random.normal(
        loc=amount_factor,
        scale=0.03,
        size=len(drift)
    )


    # 6. Small population-wide feature drift

    # Only a small change, so the simulation remains realistic.

    drift["V4"] += np.random.normal(
        loc=0.03 * month,
        scale=0.05,
        size=len(drift)
    )

    drift["V8"] -= np.random.normal(
        loc=0.025 * month,
        scale=0.05,
        size=len(drift)
    )

    return drift