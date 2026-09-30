import re
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

import httpx
from bs4 import BeautifulSoup

from app.scraper.base import BaseScraper, ScrapedJob, normalize_locations

load_dotenv()
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")


class AdzunaScraper(BaseScraper):
    def scrape(self, keyword: str, location: str = "") -> list[ScrapedJob]:
        print(f"Buscando '{keyword}' en Adzuna...")
        
        jobs_found = []

        url = f"https://api.adzuna.com/v1/api/jobs/es/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_API_KEY}&results_per_page=20"
        
        respuesta = requests.get(url, headers={"Accept": "application/json"})
        
        data = respuesta.json()
        
        ofertas = data.get("results", [])
        
        for item in ofertas:
            try:
                description = item.get("description", "")[:5000] + "..." if len(item.get("description", "")) > 5000 else item.get("description", "")

                fecha_pub = item.get("created", "")
                if fecha_pub:
                    # Convertimos el string a objeto datetime
                    try:
                        fecha_limpia = fecha_pub.replace("Z", "")
                        published_at = datetime.fromisoformat(fecha_limpia)
                    except:
                        published_at = datetime.now()
                else:
                    published_at = datetime.now()

                # Tomamos el salario máximo y mínimo
                if item.get("salary_is_predicted", False)== '0':
                    salary_min = None
                    salary_max = None
                    salary_currency = None
                else:
                    salary_min = item.get("salary_min", None)
                    salary_max = item.get("salary_max", None)
                    salary_currency = item.get("salary_currency", None)

                employment_type = re.sub(r"_", "-", item.get("contract_time", ""))

                # Mapeamos los datos a nuestro ScrapedJob
                job = ScrapedJob(
                    title=item.get("title", "Sin título"),
                    description=description,
                    company=item.get("company_name", "No especificada").get("display_name", "No especificada") if isinstance(item.get("company_name"), dict) else item.get("company_name", "No especificada"),
                    url=item.get("redirect_url", ""),
                    source="adzuna",
                    source_id=str(item.get("id", "")),
                    locations=normalize_locations(item.get("location")),
                    role=item.get("title", "Sin título"),
                    published_at=published_at,
                    remote_type="remote",
                    employment_type=employment_type,
                    salary_min=salary_min, 
                    salary_max=salary_max,
                    salary_currency=salary_currency,
                    experience_level=None,  # Adzuna no proporciona este dato
                )

                jobs_found.append(job)
                print(f"  ✓ {job.title[:40]}... en {job.company}")

            except Exception as e:
                print(f"Error parseando oferta: {e}")

        print(f"\nSe han extraído {len(jobs_found)} ofertas limpias de Remotive.\n")
        return jobs_found

        
if __name__ == "__main__":
    scraper = AdzunaScraper()
    jobs = scraper.scrape("python", "Madrid")
    for job in jobs:
        print(job)

