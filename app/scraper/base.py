from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


def normalize_locations(value: object) -> list[str]:
    """Normalize the different location shapes returned by job portals."""
    if value is None:
        return []

    values = value if isinstance(value, list) else [value]
    locations: list[str] = []

    for item in values:
        if isinstance(item, dict):
            item = item.get("display_name") or item.get("name")
        if isinstance(item, str) and item.strip():
            locations.append(item.strip())

    return list(dict.fromkeys(locations))


class ScrapedJob(BaseModel):
    title: str
    description: str

    company: str
    url: HttpUrl
    locations: list[str] = Field(default_factory=list)
    role: str | None

    source: str  # Ej: "linkedin", "glassdoor"
    source_id: str  # El ID original de la oferta en esa web

    # Campos opcionales
    skills: list[str] = Field(default_factory=list)  # Lista de habilidades requeridas
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
