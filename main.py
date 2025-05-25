import uvicorn
from fastapi import FastAPI
from contas_a_pagar_e_receber.routers import contas_a_pagar_e_receber_router, fornecedor_cliente_router, \
    fornecedor_cliente_vs_contas
from shared.exceptions import NotFound
from shared.exceptions_handlers import not_found_exception_handler

# from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasAPagarEReceberModel


# Forma antiga de manipular o banco de dados sem Alembic
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.include_router(contas_a_pagar_e_receber_router.router, prefix="/contas-a-pagar-e-receber", tags=["Contas a Pagar e Receber"])
app.include_router(contas_a_pagar_e_receber_router.router)
app.include_router(fornecedor_cliente_router.router)
app.include_router(fornecedor_cliente_vs_contas.router)
app.add_exception_handler(NotFound, not_found_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)