from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from shared.database import Base
from shared.dependencies import get_db

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db  # type: ignore


def test_deve_listar_fornecedores_clientes():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})
    response = client.get("/fornecedor-cliente")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_deve_listar_fornecedores_clientes_apenas_com_id():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})
    assert response.status_code == 201

    id_fornecedor_cliente_criado = response.json()["id"]

    response = client.get(f"/fornecedor-cliente/{id_fornecedor_cliente_criado}")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "nome": "Fornecedor 1"
    }


def test_deve_retornar_erro_404_fornecedor_cliente_nao_encontrada():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.get("/fornecedor-cliente/999")
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Fornecedor ou cliente com ID 999 não encontrado. não '
                                          'encontrado(a).'}


def test_deve_cadastrar_fornecedor_cliente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "nome": "Fornecedor 1"
    }


def test_deve_retornar_erro_422_fornecedor_cliente_invalido():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={"nome": "F"})
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'min_length': 3},
                'input': 'F',
                'loc': ['body', 'nome'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short'
            }
        ]
    }


def test_deve_retornar_erro_422_fornecedor_cliente_invalido_sem_nome():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={})
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {'input': {},
             'loc': ['body', 'nome'],
             'msg': 'Field required',
             'type': 'missing'
             }
        ]
    }


def test_deve_retornar_erro_422_fornecedor_cliente_invalido_nome_vazio():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={"nome": ""})
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'min_length': 3},
                'input': '',
                'loc': ['body', 'nome'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short'
            }
        ]
    }


def test_deve_atualizar_fornecedor_cliente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})
    assert response.status_code == 201
    id_fornecedor_cliente_criado = response.json()["id"]

    response = client.put(f"/fornecedor-cliente/{id_fornecedor_cliente_criado}", json={"nome": "Fornecedor Atualizado"})
    assert response.status_code == 200
    assert response.json() == {
        "id": id_fornecedor_cliente_criado,
        "nome": "Fornecedor Atualizado"
    }


def test_deve_retornar_erro_404_ao_atualizar_fornecedor_cliente_nao_encontrado():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.put("/fornecedor-cliente/999", json={"nome": "Fornecedor Atualizado"})
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Fornecedor ou cliente com ID 999 não encontrado. não '
                                          'encontrado(a).'}


def test_deve_deletar_fornecedor_cliente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})
    assert response.status_code == 201
    id_fornecedor_cliente_criado = response.json()["id"]

    response = client.delete(f"/fornecedor-cliente/{id_fornecedor_cliente_criado}")
    assert response.status_code == 204

    response = client.get(f"/fornecedor-cliente/{id_fornecedor_cliente_criado}")
    assert response.status_code == 404


def test_deve_retornar_erro_404_ao_deletar_fornecedor_cliente_nao_encontrado():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.delete("/fornecedor-cliente/999")
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Fornecedor ou cliente com ID 999 não encontrado. não '
                                          'encontrado(a).'}
