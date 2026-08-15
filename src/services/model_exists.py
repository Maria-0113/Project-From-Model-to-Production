from fastapi import HTTPException
from database.define_tables import ModelMetadata
from sqlalchemy.orm import Session

import logging
logger = logging.getLogger(__name__)

def model_exists(model_id:str, db: Session):
    """
    Check if a model with the given model_id exists in the database.
    If the model does not exist, raise an HTTPException with a 404 status code.

    Args:
        model_id (str): The ID of the model to check.
        db (Session): The SQLAlchemy database session.
    Returns:
        ModelMetadata: The model metadata if it exists.
    """
    logger.info(f"Checking if model with ID {model_id} exists in the database...")
    model = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    if not model:
        logger.error(f"Model with ID {model_id} not found in the database.")
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return model