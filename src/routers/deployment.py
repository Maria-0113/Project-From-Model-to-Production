from fastapi import HTTPException, Depends, APIRouter, Form
from database.connection import get_db
from database.define_tables import ModelDeployment
from sqlalchemy.orm import Session
from auth.authz import require_scope
from database.define_tables import APIKey
from services.deploy_model import deploy_model

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/deploy",
    tags=["Deployment"]
)



@router.post("")
def deploy(model_id: str = Form(...), db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("models:create"))):

    try:
        deploy_model(model_id=model_id, db=db)
    except Exception as e:
        logger.error(f"Error occurred while deploying model: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while deploying model:{e}")

    return {"status": "successfully deployed", "model_id": model_id}

@router.get("")
def get_deploy(db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("models:read"))):
    logger.info("Getting the history of models delpoyed here...")
    history = db.query(ModelDeployment).all()
    return {"history of deployed models": history}