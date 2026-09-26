from fastapi.testclient import TestClient
from app.api.api import app

# Instanciaos un cliente de prueba pasándole nuestra app de FastAPI
client = TestClient(app)

def test_get_jobs_status_and_structure() -> None:
    """
    Verifica que el endpoint /api/jobs responde correctamente
    y devuelve una lista, respetando el límite por defecto.
    """
    response = client.get("/api/jobs")

    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10  
    
    
def test_get_jobs_custom_limit() -> None:
    """
    Verifica que el endpoint /api/jobs respeta el límite personalizado.
    """
    response = client.get(f"/api/jobs?limit=3")

    assert response.status_code == 200
    
    data = response.json()
    assert len(data) <= 3
    
def test_get_jobs_filter_by_role():
    """
    Verifica que el filtro 'role' funciona y busca dentro del título.
    """
    # Buscamos un rol que sabemos que existe por nuestro scraper (ej. "developer" o "python")
    response = client.get("/api/jobs?role=developer")
    assert response.status_code == 200
    
    data = response.json()
    if len(data) > 0:
        # Comprobamos que "developer" está en el título (ignorando mayúsculas)
        assert "developer" in data[0]["title"].lower()

def test_get_jobs_filter_by_location():
    """
    Verifica que el filtro 'location' funciona correctamente.
    """
    response = client.get("/api/jobs?location=madrid")
    assert response.status_code == 200
    
    data = response.json()
    if len(data) > 0:
        assert "madrid" in data[0]["location"].lower()

def test_get_jobs_invalid_limit_validation():
    """
    Verifica que FastAPI devuelve un error 422 si le pasamos
    un tipo de dato incorrecto (texto en lugar de número).
    Este es el error que descubriste manualmente.
    """
    # Pasamos texto ("tres") en lugar de un número (3)
    response = client.get("/api/jobs?limit=tres")
    
    assert response.status_code == 422
    
def test_get_job_by_id():
    """
    Verifica que el endpoint /api/jobs/{job_id} devuelve los detalles de una oferta de trabajo por su ID.
    """
    response = client.get("/api/jobs/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == 1
    
def test_get_job_by_id_not_found():
    """
    Verifica que el endpoint /api/jobs/{job_id} devuelve un error 404 si no encuentra la oferta.
    """
    response = client.get("/api/jobs/99999999")  # Suponiendo que este ID no existe
    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}