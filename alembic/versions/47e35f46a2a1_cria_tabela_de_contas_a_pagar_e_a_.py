"""Cria tabela de Contas a Pagar e a Receber

Revision ID: 47e35f46a2a1
Revises: 
Create Date: 2025-05-21 15:07:13.772317

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '47e35f46a2a1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contas_a_pagar_e_receber',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('descricao', sa.String(length=30), nullable=True),
                    sa.Column('valor', sa.Numeric(), nullable=True),
                    sa.Column('tipo', sa.String(length=30), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contas_a_pagar_e_receber')
    # ### end Alembic commands ###
