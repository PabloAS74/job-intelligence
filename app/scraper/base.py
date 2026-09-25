from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ScrapedJob(BaseModel):
    title: str
    description: str

    company: str
    url: HttpUrl
    location: Optional[str]
    role: Optional[str]

    source: str  # Ej: "linkedin", "glassdoor"
    source_id: str  # El ID original de la oferta en esa web

    # Campos opcionales
    skills: List[str] = []  # Lista de habilidades requeridas
    remote_type: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None

    published_at: Optional[datetime]


class BaseScraper(ABC):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @abstractmethod
    def scrape(self, keyword: str, location: str = "") -> List[ScrapedJob]:
        pass
