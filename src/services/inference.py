import pandas as pd
from .validate_columns import validate_columns
import numpy as np
from .load_model import load_model

import logging
logger = logging.getLogger(__name__)


def predict(model_id: str, transaction_data: pd.DataFrame):
    """
    Run fraud predictions on a batch of transactions using a previously trained model.

    Loads the model identified by `model_id` (via an in-memory cache to avoid
    repeated disk reads), validates that `transaction_data` contains exactly
    the feature columns the model was trained on, then generates class
    predictions and class probabilities for each row.

    Args:
        model_id (str): UUID of the trained model to load and use for
            predictions (corresponds to a "<model_id>.joblib" file).
        transaction_data (pd.DataFrame): Input rows to predict on. 

    Returns:
        dict: {
            "full_data" (list[dict]): The original input rows, each with an
                added "prediction" field, as a list of row-wise records,
            "predictions" (list[int]): Predicted class labels (0 or 1) per row,
            "probabilities" (list[list[float]]): Per-class predicted
                probabilities for each row (rounded to 3 decimal places)
        }
    """
    model = load_model(model_id)

    #### Checking if the input data has the expected columns
    expected_columns = list(model.feature_names_in_)
    validate_columns(transaction_data, expected_columns)

    logger.info(f"Running predictions for model {model_id} on {len(transaction_data)} rows...")
    predictions = model.predict(transaction_data)
    probabilities = model.predict_proba(transaction_data)
    probabilities = np.round(probabilities, 3) #rounding the probabilities to 3 decimal places for better readability

    results = transaction_data.copy()
    results["prediction"] = predictions # Add prediction for each row

    return {
        "full_data": results.to_dict(orient="records"), 
        "predictions": predictions.tolist(), 
        "probabilities": probabilities.tolist()
    }