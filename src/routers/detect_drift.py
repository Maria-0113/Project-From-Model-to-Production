from fastapi import HTTPException, APIRouter
from fastapi import Depends
from services.detect_drift import detect_drift, any_csv
from services.handle_datasets import move_data
from auth.authz import require_scope
from database.define_tables import APIKey


import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/detect-drift",
    tags=["Drift Detection"]
)

@router.post("")
def detect_drift_endpoint(api_key: APIKey = Depends(require_scope("models:create")), relocate_data: bool = True):
    reference_df = any_csv("data/production")
    current_df = any_csv("data/incoming")
    if reference_df is None:
        print("No reference data found in src/data/production.")
        is_drifted = True
    else:
        drift_report, is_drifted = detect_drift(reference_df, current_df)
        print(is_drifted)
    # Relocate data if drift detected
    if relocate_data:
        move_data(is_drifted)
    return is_drifted
    