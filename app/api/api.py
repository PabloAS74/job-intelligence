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
def get_jobs(
    limit: int = 10,
    role: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db),
    ):
    """
    Devuelve una lista de ofertas de trabajo.
    Puedes cambiar el límite añadiendo ?limit=20 en la URL.
    """
    # Consulta base
    query = db.query(Job)
    
    if role:
        query = query.filter(Job.title.ilike(f"%{role}%"))
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    # Ejecutamos la consulta
    ofertas = query.limit(limit).all()

    return ofertas