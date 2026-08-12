from fastapi import HTTPException
import pandas as pd

import logging
logger = logging.getLogger(__name__)

def validate_columns(df: pd.DataFrame, expected_columns: list[str]) -> None:
    """
    Validate that the DataFrame has the expected columns.
    If the DataFrame is missing any expected columns, raise an HTTPException with a 422 status code and a detailed error message.
    """
    logger.info("Validating that the DataFrame has the expected columns...")
    expected_columns = [str(c) for c in expected_columns] #in case it's a np.str_
    df_columns = set(df.columns) #turn into a set for a fast, order-independent comparison
    expected = set(expected_columns)

    missing = sorted(expected - df_columns) #turn back into a list for a more consistent, user-friendly output
    extra = sorted(df_columns - expected)
    logger.info(f"Missing columns: {missing}")
    logger.info(f"Extra columns: {extra}")
    if missing:
        logger.error(f"CSV is missing required columns: {missing}.")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_schema",
                "message": "CSV is missing required columns.",
                "missing_columns": missing,
                "extra_columns": extra,  # optional, but helpful context
                "expected_columns": expected_columns,
            },
        )