from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#connect to the PostgreSQL server
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://ml_user1:my_password@localhost:5432/ml_database")
engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# to be able to create a fresh session per request that's properly closed afterward
#instead of using one session for the entire app. 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()