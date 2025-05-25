# config.py

import os

# Substitua pelos dados reais do seu PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:p0w2i8@localhost:5432/CursoFastApiAndersonRocha"
)
