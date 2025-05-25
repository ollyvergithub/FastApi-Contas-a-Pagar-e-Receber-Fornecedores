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


def test_deve_listar_contas_a_pagar_e_receber_com_fornecedor_cliente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response_fornecedor = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})
    id_do_fornecedor_cliente = response_fornecedor.json()["id"]

    nova_conta = {
        "descricao": "Conta de Teste",
        "valor": 100.0,
        "tipo": "Receber",
        "data_previsao": "2025-05-23",
        "fornecedor_cliente_id": id_do_fornecedor_cliente
    }
    response_conta = client.post("/contas-a-pagar-e-receber", json=nova_conta)

    response = client.get(f"/fornecedor-cliente/{id_do_fornecedor_cliente}/contas-a-pagar-e-receber")
    assert response.status_code == 200

    assert response.json() == [
        {
            "id": response_conta.json()["id"],
            "descricao": response_conta.json()["descricao"],
            "valor": response_conta.json()["valor"],
            "tipo": response_conta.json()["tipo"],
            "data_previsao": "2025-05-23",
            "fornecedor": {
                "id": id_do_fornecedor_cliente,
                "nome": "Fornecedor 1"
            },
            'esta_baixada': False,
            'valor_baixada': None,
            'data_baixa': None
        }
    ]

    assert isinstance(response.json(), list)


def test_deve_retornar_lista_vazia_contas_a_pagar_e_receber_sem_fornecedor_cliente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.get("/fornecedor-cliente/999/contas-a-pagar-e-receber")
    assert response.status_code == 200
    assert response.json() == []
