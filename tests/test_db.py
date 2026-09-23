from app.db.models import Company, Role

def test_create_and_read_entities(db_session):
    nueva_empresa = Company(name="Test Company", website="https://testcompany.com")
    db_session.add(nueva_empresa)
    db_session.commit()
    
    empresa_guardada = db_session.query(Company).filter_by(name="Test Company").first()

    assert empresa_guardada is not None 
    assert empresa_guardada.name == "Test Company"
    assert empresa_guardada.website == "https://testcompany.com"
    assert empresa_guardada.id == 1
        
def test_clean_db(db_session):
    # Al ser una session distinta la empresa ya no debería existir en la base de datos
    empresas = db_session.query(Company).all()
    assert len(empresas) == 0