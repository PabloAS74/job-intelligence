from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.db.models import Job, Role, Location
from app.schemas.response_schemas import JobResponse, JobDetailedResponse

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
        query = query.join(Job.role).filter(Role.name.ilike(f"%{role}%"))
    
    if location:
        query = query.join(Job.location).filter(Location.city.ilike(f"%{location}%"))

    # Ejecutamos la consulta
    ofertas = query.limit(limit).all()

    return ofertas


@app.get("/api/jobs/{job_id}", response_model=JobDetailedResponse)
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """
    Devuelve los detalles de una oferta de trabajo por su ID.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    # Si no existe lanzamos error 404 limpio
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job