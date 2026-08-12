import pandas as pd
from fastapi import HTTPException

import logging
logger = logging.getLogger(__name__)

def validate_csv(file):
    """
    Validate the uploaded CSV file. If the file is not a valid CSV or is empty, raise an HTTPException with a 400 status code
    """
    logger.info("Validating the uploaded CSV file...")

    try:
        if hasattr(file, "file"):   # FastAPI UploadFile
            df = pd.read_csv(file.file)
        else:                       # file path
            df = pd.read_csv(file)

    except Exception:
        logger.error("Invalid CSV file uploaded.")
        raise HTTPException(status_code=400, detail="Invalid CSV file")
    
    if df.empty:
        logger.error("CSV file has no rows.")
        raise HTTPException(status_code=400, detail="CSV file has no rows")
    logger.info(f"CSV file validated successfully. Number of rows: {len(df)}")
    return df