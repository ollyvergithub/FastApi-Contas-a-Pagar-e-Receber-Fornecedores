from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorClienteModel
from shared.dependencies import get_db
from shared.exceptions import NotFound

router = APIRouter(prefix="/fornecedor-cliente", tags=["Fornecedor e Cliente"])


def buscar_fornecedores_clientes_por_id(
        sessao: Session, id: int
) -> type[FornecedorClienteModel]:
    """
    Busca um fornecedor pelo ID.
    Args:
        sessao: Sessão do banco de dados
        id: ID do fornecedor
    Returns:
        FornecedorClienteModel: Fornecedor ou cliente encontrado
    """
    fornecedor_cliente = sessao.query(FornecedorClienteModel).filter(FornecedorClienteModel.id == id).first()

    if not fornecedor_cliente:
        raise NotFound(f"Fornecedor ou cliente com ID {id} não encontrado.")
    return fornecedor_cliente


class FornecedorClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(default=None, description="ID do fornecedor")
    nome: str = Field(..., description="Nome do fornecedor")


class FornecedorClienteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nome: str = Field(..., min_length=3, max_length=255, description="Nome do fornecedor")


@router.get("/", response_model=list[FornecedorClienteResponse], summary="Listar todos os fornecedores e clientes")
def listar_fornecedores_clientes(
        sessao: Session = Depends(get_db)
) -> list[type[FornecedorClienteModel]]:
    """
    Endpoint para listar todos os fornecedores e clientes.

    Args:
        sessao: Sessão do banco de dados

    Returns:
        list[FornecedorClienteResponse]: Lista de fornecedores e clientes encontrados
    """
    fornecedores_clientes = sessao.query(FornecedorClienteModel).all()
    if not fornecedores_clientes:
        raise NotFound("Nenhum fornecedor encontrado.")
    return fornecedores_clientes


@router.get("/{id}", response_model=FornecedorClienteResponse, summary="Buscar fornecedor por ID")
def listar_fornecedor_cliente_por_id(
        id: int, sessao: Session = Depends(get_db)
) -> type[FornecedorClienteModel]:
    """
    Endpoint para buscar um fornecedor cliente pelo ID.

    Args:
        id: ID do fornecedor
        sessao: Sessão do banco de dados

    Returns:
        FornecedorClienteResponse: Fornecedor ou cliente encontrado
    """
    fornecedor_cliente = buscar_fornecedores_clientes_por_id(sessao, id)
    return fornecedor_cliente


@router.post("/", response_model=FornecedorClienteResponse, summary="Cadastrar fornecedor", status_code=201)
def cadastrar_fornecedor_cliente(
        fornecedor_cliente: FornecedorClienteRequest,
        sessao: Session = Depends(get_db),
        status_code: int = 201
) -> FornecedorClienteModel:
    """
    Endpoint para cadastrar um fornecedor ou cliente.

    Args:
        fornecedor_cliente: Dados do fornecedor
        sessao: Sessão do banco de dados

    Returns:
        FornecedorClienteResponse: Fornecedor ou cliente cadastrado
    """
    novo_fornecedor_cliente = FornecedorClienteModel(**fornecedor_cliente.model_dump())
    sessao.add(novo_fornecedor_cliente)
    sessao.commit()
    sessao.refresh(novo_fornecedor_cliente)
    return novo_fornecedor_cliente


@router.put("/{id}", response_model=FornecedorClienteResponse, summary="Atualizar fornecedor")
def atualizar_fornecedor_cliente(
        id: int,
        fornecedor_cliente: FornecedorClienteRequest,
        sessao: Session = Depends(get_db)
) -> type[FornecedorClienteModel]:
    """
    Endpoint para atualizar um fornecedor ou cliente.

    Args:
        id: ID do fornecedor
        fornecedor_cliente: Dados do fornecedor
        sessao: Sessão do banco de dados

    Returns:
        FornecedorClienteResponse: Fornecedor ou cliente atualizado
    """
    fornecedor_cliente_atualizado = buscar_fornecedores_clientes_por_id(sessao, id)
    for key, value in fornecedor_cliente.model_dump().items():
        setattr(fornecedor_cliente_atualizado, key, value)
    sessao.commit()
    sessao.refresh(fornecedor_cliente_atualizado)
    return fornecedor_cliente_atualizado


@router.delete("/{id}", status_code=204, summary="Deletar fornecedor")
def deletar_fornecedor_cliente(
        id: int,
        sessao: Session = Depends(get_db)
) -> None:
    """
    Endpoint para deletar um fornecedor ou cliente.

    Args:
        id: ID do fornecedor
        sessao: Sessão do banco de dados

    Returns:
        None
    """
    fornecedor_cliente = buscar_fornecedores_clientes_por_id(sessao, id)
    sessao.delete(fornecedor_cliente)
    sessao.commit()
