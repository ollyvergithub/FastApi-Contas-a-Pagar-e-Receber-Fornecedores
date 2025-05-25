from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasAPagarEReceberModel

from contas_a_pagar_e_receber.routers.contas_a_pagar_e_receber_router import ContaAPagarEReceberResponse
from shared.dependencies import get_db

router = APIRouter(prefix="/fornecedor-cliente", tags=["Fornecedor e Cliente"])


@router.get(
    "/{id_do_fornecedor_cliente}/contas-a-pagar-e-receber",
    response_model=List[ContaAPagarEReceberResponse],
    summary="Listar todas as contas a pagar e receber de um fornecedor por ID do fornecedor"
)
def listar_todas_as_contas_a_pagar_e_receber_de_um_fornecedor_cliente(
        id_do_fornecedor_cliente: int, sessao: Session = Depends(get_db)
) -> list[type[ContasAPagarEReceberModel]]:
    """
    Endpoint para buscar todas as contas a pagar e receber de um fornecedor ou cliente.
    Args:
        id_do_fornecedor_cliente: ID do fornecedor
        sessao: Sessão do banco de dados
    Returns:
        FornecedorClienteResponse: Fornecedor ou cliente encontrado
    """

    return sessao.query(ContasAPagarEReceberModel).filter_by(fornecedor_cliente_id=id_do_fornecedor_cliente).all()