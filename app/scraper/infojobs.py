from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
import hashlib

from .base import BaseScraper, ScrapedJob


class InfoJobsScraper(BaseScraper):
    def scrape(self, keyword: str, location: str = "") -> List[ScrapedJob]:

        print(f"Abriendo navegador para buscar '{keyword}' en InfoJobs...")

        formatted_keyword = keyword.replace(" ", "-").lower()
        url = f"https://www.infojobs.net/ofertas-trabajo/{formatted_keyword}"

        jobs_found: List[ScrapedJob] = []

        with sync_playwright() as p:
            # 1. Añadimos un argumento para desactivar la bandera de "Navegador Automatizado"
            browser = p.chromium.launch(
                headless=False,  # Mantenlo en False de momento para ver si funciona
                slow_mo=50,
                args=["--disable-blink-features=AutomationControlled"],
            )

            # 2. Creamos un contexto con un User-Agent realista
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )

            page = context.new_page()

            # 3. ¡Aplicamos la capa de invisibilidad (Stealth)!
            stealth(page)

            try:
                print(f"URL: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)

                # ... (El resto de tu código sigue exactamente igual a partir de aquí) ...
                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")

                print(
                    "Título real:",
                    soup.title.get_text(strip=True) if soup.title else "Sin título",
                )

                # =====================================================
                # BUSCAR OFERTAS
                # =====================================================

                job_links = soup.find_all(
                    "a",
                    href=lambda href: (
                        href and ("/oferta-trabajo/" in href or "/oferta/" in href)
                    ),
                )

                print(f"Enlaces de ofertas encontrados: {len(job_links)}")

                # =====================================================
                # ELIMINAR DUPLICADOS
                # =====================================================

                seen_urls = set()

                for link in job_links:
                    href = link.get("href")

                    if not href:
                        continue

                    job_url = urljoin("https://www.infojobs.net", href)

                    if job_url in seen_urls:
                        continue

                    seen_urls.add(job_url)

                    # =================================================
                    # TÍTULO
                    # =================================================

                    title = link.get_text(" ", strip=True)

                    title = " ".join(title.split())

                    if not title:
                        continue

                    # =================================================
                    # CONTENEDOR DE LA OFERTA
                    # =================================================

                    container = (
                        link.find_parent("li")
                        or link.find_parent("article")
                        or link.parent
                    )

                    if container:
                        container_text = container.get_text(" ", strip=True)

                    else:
                        container_text = link.get_text(" ", strip=True)

                    container_text = " ".join(container_text.split())

                    # =================================================
                    # EMPRESA
                    # =================================================

                    company = ""

                    company_element = (
                        container.find(
                            attrs={
                                "data-testid": lambda value: (
                                    value and "company" in value.lower()
                                )
                            }
                        )
                        if container
                        else None
                    )

                    if company_element:
                        company = company_element.get_text(" ", strip=True)

                    # Si no conseguimos empresa,
                    # dejamos una cadena genérica.
                    if not company:
                        company = "No especificada"

                    # =================================================
                    # UBICACIÓN
                    # =================================================

                    job_location = location or None

                    location_element = (
                        container.find(
                            attrs={
                                "data-testid": lambda value: (
                                    value and "location" in value.lower()
                                )
                            }
                        )
                        if container
                        else None
                    )

                    if location_element:
                        extracted_location = location_element.get_text(" ", strip=True)

                        if extracted_location:
                            job_location = extracted_location

                    # =================================================
                    # SOURCE ID
                    # =================================================

                    parsed_url = urlparse(job_url)

                    source_id = hashlib.sha256(job_url.encode("utf-8")).hexdigest()[:32]

                    # =================================================
                    # DESCRIPCIÓN
                    # =================================================

                    description = container_text

                    if len(description) > 5000:
                        description = description[:5000]

                    # =================================================
                    # CREAR OBJETO
                    # =================================================

                    try:
                        job = ScrapedJob(
                            title=title,
                            description=description,
                            company=company,
                            url=job_url,
                            location=job_location,
                            role=title,
                            source="infojobs",
                            source_id=source_id,
                            skills=[],
                            remote_type=None,
                            employment_type=None,
                            experience_level=None,
                            salary_min=None,
                            salary_max=None,
                            salary_currency=None,
                            published_at=None,
                        )

                        jobs_found.append(job)

                        print(f"  ✓ {title}")

                    except Exception as e:
                        print(f"  ❌ Error creando oferta '{title}': {e}")

                print()
                print(f"✅ ¡Se han encontrado {len(jobs_found)} ofertas!")

            except Exception as e:
                print(f"❌ Error durante el scraping: {e}")

            finally:
                browser.close()

        return jobs_found
