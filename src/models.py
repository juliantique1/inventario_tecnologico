"""Modelo de datos del inventario tecnológico."""
# region Imports
import enum

from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import declarative_base
# endregion


# region Base declarativa
Base = declarative_base()
# endregion


# region Enums de dominio
class TipoDispositivo(enum.Enum):
    LAPTOP = "Laptop"
    SMARTPHONE = "Smartphone"
    TABLET = "Tablet"
    DESKTOP = "Desktop"
    MONITOR = "Monitor"
    IMPRESORA = "Impresora"
    OTRO = "Otro"


class EstadoDispositivo(enum.Enum):
    NUEVO = "Nuevo"
    USADO = "Usado"
    EN_REPARACION = "En reparación"
    DADO_DE_BAJA = "Dado de baja"
# endregion


# region Entidad Dispositivo
class Dispositivo(Base):
    __tablename__ = "dispositivos"

    # region Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(SAEnum(TipoDispositivo, name="tipo_dispositivo"), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    numero_serie = Column(String(100), nullable=False, unique=True)
    fecha_adquisicion = Column(Date, nullable=False)
    estado = Column(
        SAEnum(EstadoDispositivo, name="estado_dispositivo"),
        nullable=False,
        default=EstadoDispositivo.NUEVO,
    )
    precio = Column(Numeric(10, 2), nullable=False)
    ubicacion = Column(String(100), nullable=False)
    # endregion

    # region Representación
    def __repr__(self):
        return (
            f"<Dispositivo id={self.id} nombre={self.nombre!r} "
            f"tipo={self.tipo.value} estado={self.estado.value}>"
        )
    # endregion
# endregion
