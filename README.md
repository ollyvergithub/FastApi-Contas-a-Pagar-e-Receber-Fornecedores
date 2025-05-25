# FastApi - Api CRUD de Contas a Pagar e a Receber e de Forncededores + Testes Unitários e de Integração

## 🥞 Stack
- [Python v3.12](https://www.python.org/doc/)
- [FastAPI v0.115.12](https://fastapi.tiangolo.com/)
- [Starlette v0.46.2](https://www.starlette.io/)
- [Pydantic v2.11.4](https://docs.pydantic.dev/)
- [SQLAlchemy v2.0.41](https://docs.sqlalchemy.org/)
- [Alembic v1.15.2](https://alembic.sqlalchemy.org/)
- [PostgreSQL v16.4](https://www.postgresql.org/docs/)
- [asyncpg v0.30.0](https://magicstack.github.io/asyncpg/)
- [Uvicorn v0.34.2](https://www.uvicorn.org/)
- [HTTPX v0.28.1](https://www.python-httpx.org/)
- [Pytest v8.3.5](https://docs.pytest.org/en/stable/)
- [Coverage.py v7.8.1](https://coverage.readthedocs.io/)

## 📁 Estrutura de Pastas
```bash
CursoFastApiAndersonRocha2/
├── alembic/ # Migrations do banco de dados gerenciadas pelo Alembic
│ ├── versions/ # Arquivos de versão (migrations) criados pelo Alembic
│ │ ├── env.py # Script de ambiente do Alembic
│ │ ├── README # Explicação do Alembic
│ │ └── script.py.mako # Template base para novas migrations
├── contas_a_pagar_e_receber/ # Módulo principal da aplicação (domínio contas e clientes)
│ ├── models/ # Modelos das entidades do domínio
│ │ ├── init.py # Permite importar os modelos como pacote
│ │ ├── contas_a_pagar_e_receber_model.py # Modelo das contas a pagar e a receber
│ │ └── fornecedor_cliente_model.py # Modelo de fornecedores e clientes
│ ├── routers/ # Rotas da API organizadas por recurso
│ │ ├── init.py # Permite importar os routers como pacote
│ │ ├── contas_a_pagar_e_receber_router.py # Endpoints de contas a pagar e a receber
│ │ ├── fornecedor_cliente_router.py # Endpoints de fornecedores e clientes
│ │ └── fornecedor_cliente_vs_contas.py # Relações entre clientes/fornecedores e contas
│ └── init.py # Permite importar o módulo como pacote
├── shared/ # Código compartilhado entre os módulos da aplicação
│ ├── init.py # Permite importar o módulo como pacote
│ ├── database.py # Configuração da conexão com o banco de dados
│ ├── dependencies.py # Dependências injetáveis (ex: sessão do banco)
│ ├── exceptions.py # Exceções customizadas usadas na API
│ └── exceptions_handlers.py # Handlers para tratar exceções customizadas
├── test/
├── init.py # Torna o diretório test um pacote Python
├── test.db # Banco de dados SQLite usado nos testes
├── contas_a_pagar_e_receber/ # Testes relacionados ao domínio de contas
│ ├── init.py # Permite importar como pacote
│ ├── test.db # Banco de dados para esse escopo de testes
│ └── routers/ # Testes de integração dos endpoints (routers)
│ │  ├── init.py # Permite importar como pacote
│ │  ├── test_integrado_contas_a_pagar_e_receber_router.py # Testes da API de contas
│ │  ├── test_integrado_fornecedor_cliente_router.py # Testes da API de fornecedores/clientes
│ │  ├── test_integrado_fornecedor_cliente_vs_contas_router.py # Testes de associação entre entidades
│ │  └── test.db # Banco de dados específico usado nesses testes
├── venv/ # Ambiente virtual com as dependências do projeto
├── .coveragerc # Arquivo de configuração do coverage.py
├── .gitignore # Arquivos e pastas ignorados pelo Git
├── alembic.ini # Configuração principal do Alembic
├── config.py # Configurações gerais da aplicação (ex: DATABASE_URL)
├── main.py # Ponto de entrada da aplicação FastAPI
├── pytest.ini # Configuração do pytest (ex: paths, filtros de warnings)
├── requirements.txt # Arquivo com as dependências do projeto
└── README.md # Documentação principal do projeto
```

## 🛠️ Configurando o projeto

Primeiro, clone o projeto:

### 🔄 via HTTPS
    $ https://github.com/ollyvergithub/FastApi-Contas-a-Pagar-e-Receber-Fornecedores.git

### 🔐 via SSH
    $ git@github.com:ollyvergithub/FastApi-Contas-a-Pagar-e-Receber-Fornecedores.git

### 🐍 Criando e ativando uma virtual env
    $ python -m venv venv
    $ source venv/bin/activate  # Linux/macOS
    $ # ou venv\Scripts\activate no Windows

### 📦 Instalando as dependências do projeto
    $ pip install -r requirements.txt 

### 🗃️ Criando um banco do dados PostgreSQL usando createdb ou utilizando seu client preferido (pgAdmin, DBeaver...)
    $ createdb --username=postgres [NomeDoSeuBanco]
    Em config.py altere para [NomeDoSeuBanco]

### ⚙️ Rodando as migrações
    $ alembic upgrade head

### ⚙️ Para criar novas as migrações
    $ alembic revision --autogenerate -m "Texto da migração"

### ⚙️ Para aplicar Rollback da última migração
    $ alembic downgrade -1    

### 🚀 Executando o projeto
    $ python main.py

Feito tudo isso, o projeto estará executando no endereço [localhost:8001](http://localhost:8001).  
A documentação da API está disponível em [localhost:8001/docs](http://localhost:8001/docs) ou [localhost:8001/redoc](http://localhost:8001/redoc).

### 🧪 Executando os testes com Pytest
    $ pytest

### 🧪 Executando a cobertura dos testes
    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html
