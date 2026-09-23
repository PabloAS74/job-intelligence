from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///app/db/job_intelligence.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo = True,
    connect_args={"check_same_thread": False} # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()