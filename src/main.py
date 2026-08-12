from fastapi import FastAPI, Depends
from routers.models import router as models_router
from routers.predictions import router as predictions_router
from routers.health import router as health_router
from routers.deployment import router as deploy_router
from routers.detect_drift import router as detect_drift_router

from database.define_tables import Base
from database.connection import engine

import time
import logging
#logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI()


logger = logging.getLogger("api.requests")

@app.middleware("http")
async def log_requests(request, call_next):
    
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)")
    return response

#creating tables
Base.metadata.create_all(bind=engine)

app.include_router(models_router)
app.include_router(predictions_router)
app.include_router(deploy_router)
app.include_router(health_router)
app.include_router(detect_drift_router)

