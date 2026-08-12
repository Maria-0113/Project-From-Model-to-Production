from fastapi import HTTPException, UploadFile, File, Form, APIRouter
from services.inference import predict
import uuid
import json


from database.connection import get_db
from database.define_tables import Inference
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.responses import StreamingResponse
import io
from services.validate_csv import validate_csv
from services.model_exists import model_exists
from auth.authz import require_scope
from database.define_tables import APIKey, ModelDeployment
from datetime import datetime, timezone 
import time

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)

@router.post("")
def predictions(file: UploadFile = File(...), db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("predictions:create"))):

    start = time.time()
    model_id = None
    ##retrieving the currently active model from the database
    active_model = db.query(ModelDeployment).filter_by(is_active=True).first()
    if not active_model:
        raise HTTPException(status_code=404, detail="No active model found")
    model_id = active_model.model_id


    df = validate_csv(file)

    ##Run the predictions
    try: 
        result = predict(model_id=model_id, transaction_data=df)
    except Exception as e:
        logger.error(f"Error occurred while making prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while making prediction:{e}")

    ##save the predictions in the database
    logger.info("Saving predictions to the database...")
    latency_ms = (time.time() - start) * 1000
    inferenced_at = datetime.now(timezone.utc) 
    for datapoint in result["full_data"]:
        new_dict = {k: v for k, v in datapoint.items() if k != "prediction"}
        row = Inference(
            id = str(uuid.uuid4()),
            model_id=model_id, 
            features= new_dict, 
            prediction=datapoint["prediction"], 
            latency_ms = latency_ms,
            timestamp = inferenced_at
        )
        db.add(row)
    
    try:
        db.commit()
    except Exception:
        logger.error("Failed to save predictions to the database. Rolling back the transaction.")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save predictions")

    return {"predictions": result["probabilities"]}


def _export_predictions(predictions, filename):
    data = [{"id": p.id, "model_id": p.model_id, "features": p.features, "prediction": p.prediction, "timestamp": p.timestamp, "latency_ms": p.latency_ms} for p in predictions]
    buffer = io.StringIO()
    json.dump(data, buffer, indent=4, default=str)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/json",
                              headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.get("/export")   #return all predictions made by all models
def get_all_predictions(db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("predictions:read"))):

    logger.info("Exporting all predictions from the database...")
    return _export_predictions(db.query(Inference).all(), "all_predictions.json")


@router.get("/export/{model_id}")   #return all predictions made by a specific model
def get_predictions(model_id: str, db: Session = Depends(get_db), api_key: APIKey = Depends(require_scope("predictions:read"))):
    ##check whether the model exists in the database
    model_exists(model_id=model_id, db=db)

    logger.info(f"Exporting predictions for model_id: {model_id} from the database...")
    predictions = db.query(Inference).filter(Inference.model_id == model_id).all()
    return _export_predictions(predictions, f"{model_id}_predictions.json")

