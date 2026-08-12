from fastapi import HTTPException, Depends, UploadFile, File, APIRouter, Form
from services.train_model import train_model


from database.connection import get_db
from database.define_tables import ModelMetadata, ModelDeployment
from sqlalchemy.orm import Session
from services.validate_csv import validate_csv
from services.model_exists import model_exists
from auth.authz import require_scope
from database.define_tables import APIKey
from services.deploy_model import deploy_model
from services.compare_models import compare_models
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/models",
    tags=["Models"]
)

@router.post("")
def train(db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("models:create"))):
    #### take the file from the production folder. 
    production_file_path = Path("data/production")
    csv_file = next(production_file_path.glob("*.csv"))
    df = validate_csv(csv_file)
    dataset_version = "dataset_v1"
    #training the model
    try:
        metadata = train_model(df, dataset_version)
    except Exception as e:
        logger.error(f"Error occurred while training model: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while training model:{e}")

    #saving model metadata in the database
    logger.info("Saving model metadata to the database...")
    row = ModelMetadata(
        id=metadata["id"],
        trained_on=csv_file.name,
        trained_time=metadata["trained_time"],
        precision=metadata["precision"],
        recall=metadata["recall"],
        f1=metadata["f1"],
        auc=metadata["auc"],
        pr_auc=metadata["pr_auc"]
    )

    db.add(row)
    try:
        db.commit()
    except Exception:
        logger.error("Failed to save metadata in the database. Rolling back the transaction.")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save metadata in the database")
    
    try:
        logger.info("Comparing the evaluation with the deployed model...")
        result, comparison = compare_models(metadata["id"], dataset_version, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while comparing the new model perfomance with the deployed one:{e}")
    
    return {"status": "successfully trained", "model_id": metadata["id"], "is_better": result, "comparison": comparison}

@router.get("")   #return all trained models' metadata
def get_models(db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("models:read"))):
    logger.info("Fetching all models metadata from the database...")
    models_metadata = db.query(ModelMetadata).all()

    return {"models metadata": models_metadata}

@router.get("/{model_id}")   #return specific trained model's metadata
def get_model(model_id: str, db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("models:read"))):
    logger.info(f"Fetching metadata for model_id: {model_id} from the database...")
    model_metadata = model_exists(model_id=model_id, db=db)

    return {"model metadata": model_metadata}
