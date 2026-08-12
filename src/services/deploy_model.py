from database.define_tables import ModelDeployment
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from .model_exists import model_exists


import logging
logger = logging.getLogger(__name__)


def deploy_model(model_id: str, db: Session) -> ModelDeployment:
    """
    Deploys the model with the given model_id, deactivating any
    currently active model. Both operations happen in a single
    transaction so the app is never left with zero or multiple
    active models.
    """
    # verify the model actually exists before deploying it
    model_exists(model_id=model_id, db=db)

    # Deactivate whatever is currently active (if anything)
    db.query(ModelDeployment).filter_by(is_active=True).update(
        {"is_active": False}
    )

    # Activate the requested model
    new_deployment = ModelDeployment(model_id=model_id, is_active=True)
    db.add(new_deployment)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Deployment conflict for model_id {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another deployment is in progress, please retry.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deploy model with id {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy model with id {model_id}",
        )

    db.refresh(new_deployment)
    logger.info(f"Model with id {model_id} has been successfully deployed.")
    return new_deployment