from datetime import datetime

from app.db.database import SessionLocal, engine
from app.db.models import Company, Job, Location, Role, Base
from app.scraper.remotive import RemotiveScraper


def guardar_en_bd(ofertas):
    db = SessionLocal()
    try:
        nuevas_ofertas = 0

        for oferta in ofertas:
            # Buscar si la Empresa ya existe; si no, la creamos
            empresa = db.query(Company).filter_by(name=oferta.company).first()
            if not empresa:
                empresa = Company(name=oferta.company)
                db.add(empresa)
                db.flush()  # flush() asiga un ID a la empresa sin hacer commit final todavía

            # Buscar si el Rol ya existe; si no, lo creamos
            rol = db.query(Role).filter_by(name=oferta.role).first()
            if not rol:
                rol = Role(
                    name=oferta.role,
                    normalized_name=oferta.role.lower().replace(" ", "-"),
                )
                db.add(rol)
                db.flush()

            # Buscar si location ya existe; si no, lo creamos
            location = db.query(Location).filter_by(city=oferta.location).first()
            if not location:
                location = Location(city=oferta.location)
                db.add(location)
                db.flush()

            # Comprobar si la oferta ya existe para no insertar duplicados
            oferta_existente = (
                db.query(Job)
                .filter_by(source=oferta.source, source_id=oferta.source_id)
                .first()
            )

            if not oferta_existente:
                # Insertar la nueva oferta relacionándola con la empresa y el rol
                nuevo_job = Job(
                    title=oferta.title,
                    description=oferta.description,
                    role_id=rol.id,
                    company_id=empresa.id,
                    location_id=location.id,
                    remote_type=oferta.remote_type,
                    employment_type=oferta.employment_type,
                    experience_level=oferta.experience_level,
                    salary_min=oferta.salary_min,
                    salary_max=oferta.salary_max,
                    salary_currency=oferta.salary_currency,
                    published_at=oferta.published_at,
                    first_seen_at=datetime.now(),
                    last_seen_at=datetime.now(),
                    source=oferta.source,
                    source_id=oferta.source_id,
                    url=str(
                        oferta.url
                    ),  # Lo pasamos a string por si Pydantic lo tiene como HttpUrl
                )
                db.add(nuevo_job)
                nuevas_ofertas += 1

        # 5. Guardamos todos los cambios de golpe
        db.commit()
        print(
            f"\nSincronización completada: {nuevas_ofertas} ofertas nuevas guardadas en la base de datos."
        )

    except Exception as e:
        db.rollback()
        print(f"\nError al guardar en la base de datos: {e}")
    finally:
        db.close()


def main():
    
    # Esta línea crea todas las tablas si no existen. Si ya existen, no hace nada.
    Base.metadata.create_all(bind=engine)
    
    scraper = RemotiveScraper()
    ofertas = scraper.scrape("python")

    print(f"\n¡Se han extraído {len(ofertas)} ofertas limpias!")

    # Pasamos las ofertas a nuestra nueva función
    if ofertas:
        guardar_en_bd(ofertas)


if __name__ == "__main__":
    main()
