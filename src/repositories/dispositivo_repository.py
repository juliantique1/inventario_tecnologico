"""Implementación del repositorio de dispositivos usando SQLAlchemy."""
from __future__ import annotations

# region Imports
from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import Dispositivo, EstadoDispositivo, TipoDispositivo
from src.repositories.base_repository import IDispositivoRepository
from src.validation.dispositivo_validator import ValidationError
# endregion


# region DispositivoRepository
class DispositivoRepository(IDispositivoRepository):
    """Acceso a datos de dispositivos sobre una sesión de SQLAlchemy."""

    # region Constructor
    def __init__(self, session: Session):
        self._session = session
    # endregion

    # region Lectura
    def listar_todos(self) -> list[Dispositivo]:
        return self._session.query(Dispositivo).order_by(Dispositivo.id).all()

    def obtener_por_id(self, id_dispositivo: int) -> Dispositivo | None:
        return self._session.get(Dispositivo, id_dispositivo)

    def buscar(
        self,
        nombre: str | None = None,
        marca: str | None = None,
        tipo: TipoDispositivo | None = None,
        estado: EstadoDispositivo | None = None,
    ) -> list[Dispositivo]:
        query = self._session.query(Dispositivo)
        if nombre:
            query = query.filter(Dispositivo.nombre.ilike(f"%{nombre}%"))
        if marca:
            query = query.filter(Dispositivo.marca.ilike(f"%{marca}%"))
        if tipo:
            query = query.filter(Dispositivo.tipo == tipo)
        if estado:
            query = query.filter(Dispositivo.estado == estado)
        return query.order_by(Dispositivo.id).all()

    def filtrar(
        self,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
        ubicacion: str | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Dispositivo]:
        query = self._session.query(Dispositivo)
        if precio_min is not None:
            query = query.filter(Dispositivo.precio >= precio_min)
        if precio_max is not None:
            query = query.filter(Dispositivo.precio <= precio_max)
        if ubicacion:
            query = query.filter(Dispositivo.ubicacion.ilike(f"%{ubicacion}%"))
        if fecha_desde is not None:
            query = query.filter(Dispositivo.fecha_adquisicion >= fecha_desde)
        if fecha_hasta is not None:
            query = query.filter(Dispositivo.fecha_adquisicion <= fecha_hasta)
        return query.order_by(Dispositivo.id).all()
    # endregion

    # region Escritura
    def agregar(self, dispositivo: Dispositivo) -> Dispositivo:
        self._session.add(dispositivo)
        self._confirmar(dispositivo.numero_serie)
        self._session.refresh(dispositivo)
        return dispositivo

    def actualizar(self, dispositivo: Dispositivo) -> Dispositivo:
        self._confirmar(dispositivo.numero_serie)
        self._session.refresh(dispositivo)
        return dispositivo

    def eliminar(self, dispositivo: Dispositivo) -> None:
        self._session.delete(dispositivo)
        self._session.commit()
    # endregion

    # region Utilidades privadas
    def _confirmar(self, numero_serie: str) -> None:
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise ValidationError(
                f"Ya existe un dispositivo con el número de serie '{numero_serie}'."
            )
    # endregion
# endregion
