# contas_a_pagar_e_receber/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Cria a engine para conexão com o banco
engine = create_engine(DATABASE_URL, echo=True)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a classe base para os modelos
Base = declarative_base()
