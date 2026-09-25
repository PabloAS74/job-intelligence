from pydantic import BaseModel
from datetime import datetime

from app.db.models import RemoteType, EmploymentType, ExperienceLevel

class JobResponse(BaseModel):
        id: int
        title: str
        description: str | None
    
        role_id: int
        company_id: int
        location_id: int
    
        remote_type: RemoteType | None = None
        employment_type: EmploymentType | None = None
        experience_level: ExperienceLevel | None = None
        
        salary_min: int | None = None
        salary_max: int | None = None
        salary_currency: str | None = None  # Ej: EUR, USD
    
        published_at: datetime | None = None
        first_seen_at: datetime 
        last_seen_at: datetime 
    
        source: str # Ej: "linkedin", "glassdoor"
        source_id: str # El ID original de la oferta en esa web
        url: str
        
        model_config = {"from_attributes": True}