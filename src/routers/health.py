from fastapi import HTTPException, APIRouter
from database.connection import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import text

# can be used by different things (not for this project, but for example: like a load balancer, Docker healthcheck, or Kubernetes liveness probe)
# to know "is this process up and able to respond." 
# also confirms the DB is reachable. 
import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("")
def health(db: Session = Depends(get_db)):
    try:
        logger.info("Checking that db is available..")
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        logger.error("Database is unavailable.")
        raise HTTPException(status_code=503, detail="Database unavailable")