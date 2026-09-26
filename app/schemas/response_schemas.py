from pydantic import BaseModel
from datetime import datetime

from app.db.models import RemoteType, EmploymentType, ExperienceLevel


class CompanyResponse(BaseModel):
    id: int
    name: str
    website: str | None = None
    model_config = {"from_attributes": True}


class LocationResponse(BaseModel):
    id: int
    city: str
    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: int
    title: str

    role: RoleResponse
    company: CompanyResponse
    location: LocationResponse

    remote_type: RemoteType | None = None
    employment_type: EmploymentType | None = None

    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None  # Ej: EUR, USD

    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class JobDetailedResponse(JobResponse):
    """
    Extiendo JobResponse para incluir información adicional pesada.
    """

    description: str | None = None
    experience_level: ExperienceLevel | None = None

    first_seen_at: datetime
    last_seen_at: datetime

    source: str  # Ej: "linkedin", "glassdoor"
    source_id: str  # El ID original de la oferta en esa web
    url: str


class CompanyStatsResponse(BaseModel):
    company: CompanyResponse
    job_count: int
    model_config = {"from_attributes": True}
