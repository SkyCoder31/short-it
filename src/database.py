from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import get_settings

settings = get_settings()

# Create the engine
engine = create_engine(settings.database_url, pool_size=20, max_overflow=40)

#SessionLocal class (a factory for new DB sessions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# gives a database session to any endpoint that asks for it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()