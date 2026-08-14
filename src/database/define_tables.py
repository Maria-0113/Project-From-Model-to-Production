from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from datetime import timezone, datetime

#define the table
from .connection import Base

class ModelMetadata(Base):

    __tablename__ = "model_metadata"

    id = Column(String, primary_key=True)
    trained_on = Column(String)
    trained_time = Column(String)
    precision = Column(Float)
    recall = Column(Float)
    f1 = Column(Float)
    auc = Column(Float)
    pr_auc = Column(Float)

class Inference(Base):
    
    __tablename__ = "inference"
    
    id = Column(String, primary_key=True)
    model_id = Column(String)
    features = Column(JSONB)
    prediction = Column(Float)
    latency_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    client_name = Column(String, nullable=False)
    key_hash = Column(String, unique=True, index=True, nullable=False)
    scopes = Column(JSON, default=list)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime, nullable=True)

class ModelDeployment(Base):
    __tablename__ = "model_deployments"
    id = Column(Integer, primary_key=True)
    model_id = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    deployed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

