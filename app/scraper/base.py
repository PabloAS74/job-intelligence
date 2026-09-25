from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ScrapedJob(BaseModel):
    title: str
    description: str

    company: str
    url: HttpUrl
    location: str | None
    role: str | None

    source: str  # Ej: "linkedin", "glassdoor"
    source_id: str  # El ID original de la oferta en esa web

    # Campos opcionales
    skills: list[str] = []  # Lista de habilidades requeridas
    remote_type: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None

    published_at: datetime | None


class BaseScraper(ABC):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @abstractmethod
    def scrape(self, keyword: str, location: str = "") -> list[ScrapedJob]:
        pass
