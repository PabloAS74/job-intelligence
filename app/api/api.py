from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.db.models import Job
from app.schemas.response_schemas import JobResponse

# Inicializamos la API  
app = FastAPI(
    title = "Job Intelligence API",
    description = "API para consultar ofertas de trabajo extraídas",
    version = "1.0.0",
)

@app.get("/api/jobs", response_model=list[JobResponse])
def get_jobs(limit: int = 10, db: Session = Depends(get_db)):
    """
    Devuelve una lista de ofertas de trabajo.
    Puedes cambiar el límite añadiendo ?limit=20 en la URL.
    """
    return db.query(Job).limit(limit).all()