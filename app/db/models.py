from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Definición de enums
class RemoteType(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "on-site"

class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"

class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"



# Clase base
class Base(DeclarativeBase):
    pass

# Modelo Job
class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    
    remote_type: Mapped[Optional[RemoteType]] = mapped_column(String(50))
    employment_type: Mapped[Optional[EmploymentType]] = mapped_column(String(50))
    experience_level: Mapped[Optional[ExperienceLevel]] = mapped_column(String(50))

    salary_min: Mapped[Optional[int]]
    salary_max: Mapped[Optional[int]]
    salary_currency: Mapped[Optional[str]] = mapped_column(String(3)) # Ej: EUR, USD

    published_at: Mapped[Optional[datetime]]
    first_seen_at: Mapped[datetime]
    last_seen_at: Mapped[datetime]

    source: Mapped[str] = mapped_column(String(50), nullable=False) # Ej: "linkedin", "glassdoor"
    source_id: Mapped[str] = mapped_column(String(100), nullable=False) # El ID original de la oferta en esa web
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}')>"

# Modelo Company
class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"
    
# Modelo Role 
class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"
    
    
    
# Modelo Location
class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, city='{self.city}', region='{self.region}', country='{self.country}')>"
    
    
# Modelo Skill
class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    normalized_name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<Skill(id={self.id}, name='{self.name}')>"
    
    
class JobSkill(Base):
    
    __tablename__ = "job_skills"

    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)

    def __repr__(self) -> str:
        return f"<JobSkill(job_id={self.job_id}, skill_id={self.skill_id})>"