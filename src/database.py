"""Configuración de la conexión a la base de datos MySQL."""
# region Imports
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base
# endregion


# region Configuración de entorno
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "inventario_tecnologico")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
# endregion


# region Motor y fábrica de sesiones
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# endregion


# region Utilidades
def init_db():
    """Crea las tablas del modelo de datos si no existen."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Devuelve una nueva sesión de trabajo con la base de datos."""
    return SessionLocal()
# endregion
