import pytest
from app import create_app
from models import db, Usuario, Chamado, Setor
from ml_model import predict_time

@pytest.fixture
def app():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test'
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        # Seed test data
        u = Usuario(nome="Test", sobrenome="User", cpf="123", data_nascimento="2000-01-01", email_corporativo="test@test.com", perfil="Usuario")
        u.set_senha("senha123")
        db.session.add(u)
        
        s = Setor(nome="RH")
        db.session.add(s)
        
        db.session.commit()
        
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login(client):
    response = client.post('/api/auth/login', json={
        'nome': 'test@test.com',
        'senha': 'senha123'
    })
    assert response.status_code == 200
    assert b'Logado com sucesso' in response.data

def test_login_fail(client):
    response = client.post('/api/auth/login', json={
        'nome': 'test@test.com',
        'senha': 'wrongpassword'
    })
    assert response.status_code == 401

def test_predict_time():
    # Testa se o modelo ML retorna um valor numérico float/int
    time = predict_time('MANUTENÇÃO ELÉTRICA', 'ALTA', 'RH', 'BOM')
    assert isinstance(time, float) or isinstance(time, int)
    assert time > 0

def test_criar_chamado(client, app):
    # Log in first
    client.post('/api/auth/login', json={'nome': 'test@test.com', 'senha': 'senha123'})
    
    response = client.post('/api/chamados', json={
        'setor': 'RH',
        'categoria': 'CLIMATIZAÇÃO',
        'problema': 'AR CONDICIONADO COM VAZAMENTO',
        'prioridade': 'MÉDIA'
    })
    
    assert response.status_code == 200
    
    with app.app_context():
        c = Chamado.query.first()
        assert c is not None
        assert c.categoria == 'CLIMATIZAÇÃO'
        assert c.status == 'ABERTO'
        assert c.tempo_estimado > 0
