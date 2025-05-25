from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from shared.database import Base

class ContasAPagarEReceberModel(Base):
    __tablename__ = 'contas_a_pagar_e_receber'
    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(255))
    valor = Column(Numeric)
    tipo = Column(String(30))
    data_previsao = Column(Date(), nullable=False)
    data_baixa = Column(Date(), nullable=True)
    valor_baixada = Column(Numeric(), nullable=True)
    esta_baixada = Column(Boolean(), nullable=True, default=False)

    fornecedor_cliente_id = Column(Integer, ForeignKey('fornecedor_cliente.id'))
    fornecedor = relationship('FornecedorClienteModel')
