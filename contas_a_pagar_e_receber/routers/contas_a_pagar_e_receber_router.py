from datetime import date
from decimal import Decimal
from enum import Enum
from itertools import groupby
from typing import List, Any

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import extract
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasAPagarEReceberModel
from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorClienteModel
from contas_a_pagar_e_receber.routers.fornecedor_cliente_router import FornecedorClienteResponse
from shared.dependencies import get_db
from shared.exceptions import NotFound

router = APIRouter(prefix="/contas-a-pagar-e-receber", tags=["Contas a Pagar e Receber"])

QUANTIDADE_DE_CONTAS_PERMITIDA_POR_MES = 5


class ContaAPagarEReceberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    descricao: str
    valor: float
    tipo: str
    data_previsao: date
    data_baixa: date | None = None,
    valor_baixada: float | None = None,
    esta_baixada: bool | None = None
    fornecedor: FornecedorClienteResponse | None = None


class ContaPagarEReceberEnum(str, Enum):
    Pagar = "Pagar"
    Receber = "Receber"


class ContaAPagarEReceberRequest(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=255)
    valor: Decimal = Field(..., gt=0)
    tipo: str = ContaPagarEReceberEnum
    data_previsao: date
    fornecedor_cliente_id: int | None = None


class PrevisaoGastosPorMesResponse(BaseModel):
    mes: int
    valor_total: float


def buscar_todas_contas(sessao: Session) -> list[type[ContasAPagarEReceberModel]]:
    """Busca todas as contas cadastradas no banco de dados."""
    return sessao.query(ContasAPagarEReceberModel).all()


def valida_fornecedor(fornecedor_cliente_id, db):
    if fornecedor_cliente_id:
        fornecedor_cliente_existente = db.query(FornecedorClienteModel).filter_by(
            id=fornecedor_cliente_id
        ).first()

        if not fornecedor_cliente_existente:
            raise NotFound(f"Fornecedor com ID {fornecedor_cliente_id}")


def recupera_numero_de_registros(db, ano, mes) -> int:
    """Valida o número de registros no banco de dados."""
    # Implementar a lógica de validação do número de registros
    qtde_registros = (
        db.query(ContasAPagarEReceberModel)
        .filter(extract('year', ContasAPagarEReceberModel.data_previsao) == ano)
        .filter(extract('month', ContasAPagarEReceberModel.data_previsao) == mes)
        .count()
    )
    return qtde_registros


def valida_se_pode_criar_nova_conta(
        db: Session,
        contas_a_pagar_e_receber: ContaAPagarEReceberRequest,
) -> None:
    """Lança uma exceção se o limite de contas for ultrapassado."""
    if recupera_numero_de_registros(db, contas_a_pagar_e_receber.data_previsao.year,
                                    contas_a_pagar_e_receber.data_previsao.month) > QUANTIDADE_DE_CONTAS_PERMITIDA_POR_MES:
        raise HTTPException(status_code=422, detail="Limite de contas atingido para o mês")


def relatorio_gastos_previstos_por_mes_de_um_ano(
        db: Session,
        ano: int,
) -> List[PrevisaoGastosPorMesResponse]:
    """Retorna uma lista de contas a pagar e receber para um determinado mês e ano."""

    contas = (
        db.query(ContasAPagarEReceberModel)
        .filter(extract('year', ContasAPagarEReceberModel.data_previsao) == ano)
        .filter(ContasAPagarEReceberModel.tipo == ContaPagarEReceberEnum.Pagar)
        .order_by(ContasAPagarEReceberModel.data_previsao.desc())
        .all()
    )

    valor_por_mes = {}

    for conta in contas:
        mes = conta.data_previsao.month
        valor = conta.valor

        if valor_por_mes.get(mes) is None:
            valor_por_mes[mes] = 0

        valor_por_mes[mes] += valor

    for k, g in groupby(contas, lambda x: x.data_previsao.month):
        print({k: sum(v.valor for v in g)})
        # valor_por_mes2[k] = sum(conta.valor for conta in g)

    return [PrevisaoGastosPorMesResponse(mes=k, valor_total=v) for k, v in valor_por_mes.items()]



@router.get("/previsao-gastos-do-mes", response_model=List[PrevisaoGastosPorMesResponse])
def previsao_de_gastos_por_mes_do_ano(db: Session = Depends(get_db), ano=date.year):
    """
    Endpoint para gerar um relatório de gastos previstos por mês de um ano.

    Args:
        ano: Ano para o qual o relatório será gerado
        db: Sessão do banco de dados

    Returns:
        List[ContaAPagarEReceberResponse]: Relatório de gastos previstos
    """

    r = relatorio_gastos_previstos_por_mes_de_um_ano(db, ano)
    return r


@router.get(
    "/",
    response_model=List[ContaAPagarEReceberResponse],
    summary="Listar todas as contas",
    description="Retorna uma lista com todas as contas a pagar e receber cadastradas"
)
def listar_todas_contas(sessao: Session = Depends(get_db)) -> List[ContaAPagarEReceberResponse]:
    """
    Endpoint para listar todas as contas a pagar e receber.

    Args:
        sessao: Sessão do banco de dados

    Returns:
        List[ContaAPagarEReceberResponse]: Lista de contas encontradas
    """
    return buscar_todas_contas(sessao)


# @router.get("/", response_model=list[ContaAPagarEReceberResponse])
# def listar_contas(db: Session = Depends(get_db)) -> list[ContaAPagarEReceberResponse]:
#     return db.query(ContasAPagarEReceberModel).all()

# @router.get("/", response_model=list[ContaAPagarEReceberResponse])
# def listar_contas():
#     return [
#         ContaAPagarEReceberResponse(id=1, descricao="Conta 1", valor=100.0, tipo="Pagar"),
#         ContaAPagarEReceberResponse(id=2, descricao="Conta 2", valor=14016.0, tipo="Receber")
#     ]

# @router.get("/")
# def listar_contas():
#     return [{"conta1": "Conta 1"}, {"conta2": "Conta 2"}]


def buscar_conta_por_id(sessao: Session, conta_id: int) -> ContasAPagarEReceberModel:
    """Busca uma conta pelo ID."""
    contas_a_pagar_e_receber = sessao.query(ContasAPagarEReceberModel).filter_by(id=conta_id).first()

    if not contas_a_pagar_e_receber:
        raise NotFound(f"Conta com ID {conta_id} não encontrada")

    return contas_a_pagar_e_receber


@router.get("/{conta_id}", response_model=ContaAPagarEReceberResponse)
def listar_conta_por_id(
        conta_id: int,
        db: Session = Depends(get_db)
) -> ContaAPagarEReceberResponse:
    """
    Endpoint para listar uma conta a pagar ou receber pelo ID.

    Args:
        conta_id: ID da conta a ser buscada
        db: Sessão do banco de dados

    Returns:
        ContaAPagarEReceberResponse: Conta encontrada

    Raises:
        HTTPException: Se a conta não for encontrada
    """
    contas_a_pagar_e_receber = buscar_conta_por_id(db, conta_id)

    if not contas_a_pagar_e_receber:
        raise NotFound(f"Conta com ID {conta_id} não encontrada")

    return contas_a_pagar_e_receber


@router.post("/", response_model=ContaAPagarEReceberResponse, status_code=201)
def criar_conta(conta: ContaAPagarEReceberRequest, db: Session = Depends(get_db)) -> ContaAPagarEReceberResponse:
    """
    Cria uma nova conta a pagar ou receber.
    
    Args:
        conta: Dados da conta a ser criada
        db: Sessão do banco de dados
    
    Returns:
        ContaAPagarEReceberResponse: Conta criada
        
    Raises:
        HTTPException: Se houver erro na validação ou na criação
    """

    # contas_a_pagar_e_receber = ContasAPagarEReceberModel(**conta.model_dump())
    # db.add(contas_a_pagar_e_receber)
    # db.commit()
    # db.refresh(contas_a_pagar_e_receber)
    # return contas_a_pagar_e_receber

    # Verifica se o fornecedor_cliente_id existe
    valida_fornecedor(conta.fornecedor_cliente_id, db)

    # Verifica se o número de registros no mês e ano é maior que 100
    valida_se_pode_criar_nova_conta(db=db, contas_a_pagar_e_receber=conta)

    try:
        if conta.valor <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser positivo")

        if not conta.descricao.strip():
            raise HTTPException(status_code=400, detail="Descrição não pode ser vazia")

        if conta.tipo not in ["Pagar", "Receber"]:
            raise HTTPException(status_code=400, detail="Tipo deve ser 'Pagar' ou 'Receber'")

        contas_a_pagar_e_receber = ContasAPagarEReceberModel(**conta.model_dump())
        db.add(contas_a_pagar_e_receber)
        db.commit()
        db.refresh(contas_a_pagar_e_receber)
        return contas_a_pagar_e_receber

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar conta")

    # Antes de criar a classe     class Config:
    # return ContaAPagarEReceberResponse(**contas_a_pagar_e_receber.__dict__)


# @router.post("/", response_model=ContaAPagarEReceberResponse, status_code=201)
# def criar_conta(conta: ContaAPagarEReceberRequest):
#     return ContaAPagarEReceberResponse(
#         id=3, descricao=conta.descricao,
#         valor=conta.valor,
#         tipo=conta.tipo
#     )

@router.put("/{conta_id}", response_model=ContaAPagarEReceberResponse)
def atualizar_conta(
        conta_id: int,
        conta: ContaAPagarEReceberRequest,
        db: Session = Depends(get_db)
) -> ContaAPagarEReceberResponse:
    """
    Atualiza uma conta a pagar ou receber existente.

    Args:
        conta_id: ID da conta a ser atualizada
        conta: Dados atualizados da conta
        db: Sessão do banco de dados

    Returns:
        ContaAPagarEReceberResponse: Conta atualizada

    Raises:
        HTTPException: Se a conta não for encontrada ou houver erro na atualização
    """

    contas_a_pagar_e_receber = buscar_conta_por_id(db, conta_id)

    # Verifica se o fornecedor_cliente_id existe
    valida_fornecedor(conta.fornecedor_cliente_id, db)

    try:
        for key, value in conta.model_dump().items():
            setattr(contas_a_pagar_e_receber, key, value)

        db.commit()
        db.refresh(contas_a_pagar_e_receber)

        return contas_a_pagar_e_receber

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar conta")


@router.delete("/{conta_id}", status_code=204)
def deletar_conta(
        conta_id: int,
        db: Session = Depends(get_db)
) -> None:
    """
    Deleta uma conta a pagar ou receber existente.

    Args:
        conta_id: ID da conta a ser deletada
        db: Sessão do banco de dados

    Raises:
        HTTPException: Se a conta não for encontrada ou houver erro na deleção
    """

    contas_a_pagar_e_receber = buscar_conta_por_id(db, conta_id)
    db.delete(contas_a_pagar_e_receber)
    db.commit()

    # try:
    #     # contas_a_pagar_e_receber = db.query(ContasAPagarEReceberModel).filter_by(id=conta_id).first()
    #     contas_a_pagar_e_receber = buscar_conta_por_id(db, conta_id)
    #
    #     if not contas_a_pagar_e_receber:
    #         raise HTTPException(status_code=404, detail="Conta não encontrada")
    #
    #     db.delete(contas_a_pagar_e_receber)
    #     db.commit()
    #
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail="Erro ao deletar conta")


@router.post("/{conta_id}/baixar", response_model=ContaAPagarEReceberResponse, status_code=200)
def baixar_conta(
        conta_id: int,
        db: Session = Depends(get_db)
) -> ContasAPagarEReceberModel:
    contas_a_pagar_e_receber = buscar_conta_por_id(db, conta_id)
    contas_a_pagar_e_receber.data_baixa = date.today()
    contas_a_pagar_e_receber.esta_baixada = True
    contas_a_pagar_e_receber.valor_baixada = contas_a_pagar_e_receber.valor

    db.commit()
    db.refresh(contas_a_pagar_e_receber)

    return contas_a_pagar_e_receber
