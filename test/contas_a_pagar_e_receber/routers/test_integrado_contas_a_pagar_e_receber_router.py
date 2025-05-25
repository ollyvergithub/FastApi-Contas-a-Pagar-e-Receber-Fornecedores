from unittest.mock import MagicMock

import pytest
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


@pytest.fixture
def nova_conta_fixture():
    return {
        "descricao": "Conta de Teste",
        "valor": 100.0,
        "tipo": "Receber",
        "data_previsao": "2025-05-23",
    }


@pytest.fixture
def nova_conta_com_fornecedor_id_fixture(nova_conta_fixture):
    nova_conta_fixture['fornecedor_cliente_id'] = 1

    return nova_conta_fixture


@pytest.fixture
def nova_conta_retorno_fixture():
    return {
        "id": 1,
        'data_baixa': None,
        "descricao": "Conta de Teste",
        "valor": 100.0,
        "tipo": "Receber",
        'fornecedor': None,
        'esta_baixada': False,
        'valor_baixada': None,
        "data_previsao": "2025-05-23",
    }


@pytest.fixture
def nova_conta_retorno_com_fornecedor_fixture(nova_conta_retorno_fixture):
    nova_conta_retorno_fixture['fornecedor'] = {'id': 1, 'nome': 'Fornecedor 1'}

    return nova_conta_retorno_fixture


def test_deve_listar_contas_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.get("/contas-a-pagar-e-receber")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_deve_listar_contas_a_pagar_e_receber_apenas_com_id(nova_conta_fixture, nova_conta_retorno_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)
    assert response.status_code == 201

    id_conta_criada = response.json()["id"]

    response = client.get(f"/contas-a-pagar-e-receber/{id_conta_criada}")
    assert response.status_code == 200

    assert response.json() == nova_conta_retorno_fixture


def test_deve_retornar_erro_404_conta_nao_encontrada():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.get("/contas-a-pagar-e-receber/999")
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Conta com ID 999 não encontrada não encontrado(a).'}


def test_deve_criar_contas_a_pagar_e_receber(nova_conta_fixture, nova_conta_retorno_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)
    assert response.status_code == 201

    assert response.json() == nova_conta_retorno_fixture


def test_deve_criar_conta_com_fornecedor_cliente(nova_conta_com_fornecedor_id_fixture,
                                                 nova_conta_retorno_com_fornecedor_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response_fornecedor = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})

    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_com_fornecedor_id_fixture)
    assert response.status_code == 201

    assert response.json() == nova_conta_retorno_com_fornecedor_fixture


def test_deve_retornar_erro_ao_criar_conta_com_fornecedor_cliente_invalido():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {
        "descricao": "Conta de Teste",
        "valor": 100.0,
        "tipo": "Receber",
        "data_previsao": "2025-05-23",
        "fornecedor_cliente_id": 999
    }
    response = client.post("/contas-a-pagar-e-receber", json=nova_conta)
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Fornecedor com ID 999 não encontrado(a).'}


def test_deve_retornar_erro_500_ao_criar_conta_com_exception(nova_conta_fixture):
    # Cria um mock da sessão de banco
    mock_db = MagicMock()
    mock_db.commit.side_effect = Exception("Erro simulado")
    mock_db.rollback = MagicMock()
    mock_db.add = MagicMock()
    mock_db.refresh = MagicMock()

    # Configura o mock para retornar 0 na contagem de registros
    mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0

    def fake_get_db():
        yield mock_db

    # Salva o override original
    original_override = app.dependency_overrides.get(get_db)

    # Aplica o override temporário
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)

        assert response.status_code == 500
        assert response.json()["detail"] == "Erro ao criar conta"
    finally:
        # Restaura o comportamento original
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            app.dependency_overrides.pop(get_db, None)


def test_deve_atualizar_conta_a_pagar_e_receber(nova_conta_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)
    assert response.status_code == 201

    id_conta_criada = response.json()["id"]

    conta_atualizada = nova_conta_fixture.copy()

    conta_atualizada['descricao'] = "Conta Atualizada"
    conta_atualizada['valor'] = 200.0
    conta_atualizada['tipo'] = "Pagar"

    response = client.put(f"/contas-a-pagar-e-receber/{id_conta_criada}", json=conta_atualizada)
    assert response.status_code == 200

    assert response.json() == {
        "id": id_conta_criada,
        "descricao": "Conta Atualizada",
        "valor": 200.0,
        "tipo": "Pagar",
        'fornecedor': None,
        'esta_baixada': False,
        'valor_baixada': None,
        'data_baixa': None,
        "data_previsao": "2025-05-23",
    }


def test_deve_atualizar_conta_a_pagar_e_receber_com_fornecedor_cliente(nova_conta_com_fornecedor_id_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response_fornecedor = client.post("/fornecedor-cliente", json={"nome": "Fornecedor 1"})

    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_com_fornecedor_id_fixture)
    assert response.status_code == 201

    id_conta_criada = response.json()["id"]

    conta_atualizada = {
        "descricao": "Conta Atualizada",
        "valor": 200.0,
        "tipo": "Pagar",
        "data_previsao": "2025-05-23",
        "fornecedor_cliente_id": response_fornecedor.json()["id"]
    }
    response = client.put(f"/contas-a-pagar-e-receber/{id_conta_criada}", json=conta_atualizada)
    assert response.status_code == 200

    assert response.json() == {
        "id": id_conta_criada,
        "descricao": "Conta Atualizada",
        "valor": 200.0,
        "tipo": "Pagar",
        'fornecedor': {'id': response_fornecedor.json()['id'], 'nome': response_fornecedor.json()['nome']},
        'esta_baixada': False,
        'valor_baixada': None,
        'data_baixa': None,
        "data_previsao": "2025-05-23",
    }


def test_deve_retornar_erro_ao_atualizar_conta_com_fornecedor_cliente_invalido():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {
        "descricao": "Conta de Teste",
        "valor": 100.0,
        "tipo": "Receber",
        "data_previsao": "2025-05-23",
        "fornecedor_cliente_id": 999
    }
    response = client.post("/contas-a-pagar-e-receber", json=nova_conta)
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Fornecedor com ID 999 não encontrado(a).'}


def test_deve_retornar_erro_404_ao_atualizar_conta_nao_encontrada(nova_conta_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.put("/contas-a-pagar-e-receber/999", json=nova_conta_fixture)
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Conta com ID 999 não encontrada não encontrado(a).'}


def test_deve_deletar_conta_a_pagar_e_receber(nova_conta_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)
    assert response.status_code == 201
    response = client.delete("/contas-a-pagar-e-receber/1")
    assert response.status_code == 204
    response = client.get("/contas-a-pagar-e-receber/1")
    assert response.status_code == 404


def test_deve_retornar_erro_404_ao_deletar_conta_nao_encontrada():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response = client.delete("/contas-a-pagar-e-receber/999")
    assert response.status_code == 404
    assert response.json() == {'message': 'Oops! Conta com ID 999 não encontrada não encontrado(a).'}


def test_baixar_conta_a_pagar_e_receber(nova_conta_fixture):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)
    assert response.status_code == 201
    id_conta_criada = response.json()["id"]
    response = client.post(f"/contas-a-pagar-e-receber/{id_conta_criada}/baixar")
    assert response.status_code == 200
    resultado = response.json()
    assert resultado["id"] == id_conta_criada
    assert resultado["descricao"] == "Conta de Teste"
    assert float(resultado["valor"]) == 100.0  # Convertendo string para float
    assert resultado["tipo"] == "Receber"
    assert resultado["esta_baixada"] is True
    assert resultado["fornecedor"] is None
    assert isinstance(resultado["data_baixa"], str)  # Verificando se é uma string
    assert float(resultado["valor_baixada"]) == 100.0  # Convertendo string para float


def test_deve_validar_se_pode_criar_nova_conta_numero_de_contas(nova_conta_fixture):
    from contas_a_pagar_e_receber.routers.contas_a_pagar_e_receber_router import QUANTIDADE_DE_CONTAS_PERMITIDA_POR_MES
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Criar 5 contas
    for i in range(QUANTIDADE_DE_CONTAS_PERMITIDA_POR_MES + 1):
        nova_conta = {
            "descricao": f"Conta de Teste {i}",
            "valor": 100.0 + i,
            "tipo": "Receber",
            "data_previsao": "2025-05-23",
        }
        response = client.post("/contas-a-pagar-e-receber", json=nova_conta)
        assert response.status_code == 201

    # Tentar criar a 6ª conta
    nova_conta = {
        "descricao": "Conta de Teste 11",
        "valor": 1100.0,
        "tipo": "Receber",
        "data_previsao": "2025-05-23",
    }
    response = client.post("/contas-a-pagar-e-receber", json=nova_conta_fixture)
    assert response.status_code == 422
    assert response.json() == {'detail': 'Limite de contas atingido para o mês'}


def test_previsao_de_gastos_por_mes():
    from contas_a_pagar_e_receber.routers.contas_a_pagar_e_receber_router import QUANTIDADE_DE_CONTAS_PERMITIDA_POR_MES
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Criar 5 contas
    for i in range(QUANTIDADE_DE_CONTAS_PERMITIDA_POR_MES + 1):
        nova_conta = {
            "descricao": f"Conta de Teste {i}",
            "valor": 100.0 + i,
            "tipo": "Pagar",
            "data_previsao": "2025-05-23",
        }
        response = client.post("/contas-a-pagar-e-receber", json=nova_conta)
        assert response.status_code == 201

    response = client.get("/contas-a-pagar-e-receber/previsao-gastos-do-mes?ano=2025")
    assert response.status_code == 200
    assert response.json() == [
        {
            "mes": 5,
            "valor_total": 615.0
        },
    ]


def test_previsao_de_gastos_por_mes_sem_lancamentos():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


    response = client.get("/contas-a-pagar-e-receber/previsao-gastos-do-mes?ano=2025")
    assert response.status_code == 200
    assert response.json() == []