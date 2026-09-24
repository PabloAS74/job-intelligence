import httpx
from typing import List
import re
from .base import BaseScraper, ScrapedJob
from datetime import datetime

class RemotiveScraper(BaseScraper):
    def scrape(self, keyword: str, location: str = "") -> List[ScrapedJob]:
        print(f"Buscando '{keyword}' en Remotive...")
        
        # Usamos la API oficial de Remotive
        url = f"https://remotive.com/api/remote-jobs?search={keyword}"
        
        jobs_found = []
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return []
                
            data = response.json()
            ofertas = data.get("jobs", [])
            
            for item in ofertas:
                try:
                    # Recortamos la descripción 
                    description = item.get("description", "")
                    if len(description) > 5000:
                        description = description[:5000] + "..."

                    fecha_pub = item.get("publication_date")
                    if fecha_pub:
                        # Convertimos el string a objeto datetime
                        try:
                            fecha_limpia = fecha_pub.replace('Z', '')
                            published_at = datetime.fromisoformat(fecha_limpia)
                        except:
                            published_at = datetime.now()
                    else:
                        published_at = datetime.now()

                    # Tomamos el salario máximo y mínimo
                    salary = re.search(r"\$(\d+)k\s*-\s*\$(\d+)k", item.get("salary", ""))
                    if salary:
                        salary_min = int(salary.group(1)) * 1000
                        salary_max = int(salary.group(2)) * 1000

                    # Mapeamos los datos a nuestro ScrapedJob
                    job = ScrapedJob(
                        title=item.get("title", "Sin título"),
                        description=description,
                        company=item.get("company_name", "No especificada"),
                        url=item.get("url", ""),
                        source="remotive",
                        source_id=str(item.get("id", "")),
                        location=item.get("candidate_required_location", "No especificada"),
                        role=item.get("title", "Sin título"), 
                        published_at=published_at,
                        remote_type="100% Remote",
                        employment_type=item.get("job_type", ""),
                        salary_min=salary_min if salary else None,
                        salary_max=salary_max if salary else None,
                        salary_currency="USD" if salary else None,
                        experience_level=None,  # Remotive no proporciona este dato
                    )
                    
                    jobs_found.append(job)
                    print(f"  ✓ {job.title[:40]}... en {job.company}")
                    
                except Exception as e:
                    print(f"Error parseando oferta: {e}")
                    
        print(f"\nSe han extraído {len(jobs_found)} ofertas limpias de Remotive.\n")
        return jobs_found