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