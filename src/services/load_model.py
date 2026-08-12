import logging
import joblib
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=8) # Cache the loaded models to avoid reloading them from disk for every prediction
def load_model(model_id: str):
    logger.info(f"Loading model {model_id} from cache or disk...")
    try:
        return joblib.load(f"models/{model_id}.joblib")
    except FileNotFoundError:
        logger.error(f"Model file .joblib for {model_id} not found on disk")
        raise ValueError(f"Model file .joblib for {model_id} not found on disk")