"""Contratos (interfaces) para el acceso a datos de dispositivos."""
from __future__ import annotations

# region Imports
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from src.models import Dispositivo, EstadoDispositivo, TipoDispositivo
# endregion


# region Lector de dispositivos
class IDispositivoLector(ABC):
    """Operaciones de solo lectura sobre el inventario."""

    @abstractmethod
    def listar_todos(self) -> list[Dispositivo]: ...

    @abstractmethod
    def obtener_por_id(self, id_dispositivo: int) -> Dispositivo | None: ...

    @abstractmethod
    def buscar(
        self,
        nombre: str | None = None,
        marca: str | None = None,
        tipo: TipoDispositivo | None = None,
        estado: EstadoDispositivo | None = None,
    ) -> list[Dispositivo]: ...

    @abstractmethod
    def filtrar(
        self,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
        ubicacion: str | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Dispositivo]: ...
# endregion


# region Escritor de dispositivos
class IDispositivoEscritor(ABC):
    """Operaciones de escritura sobre el inventario."""

    @abstractmethod
    def agregar(self, dispositivo: Dispositivo) -> Dispositivo: ...

    @abstractmethod
    def actualizar(self, dispositivo: Dispositivo) -> Dispositivo: ...

    @abstractmethod
    def eliminar(self, dispositivo: Dispositivo) -> None: ...
# endregion


# region Repositorio completo
class IDispositivoRepository(IDispositivoLector, IDispositivoEscritor, ABC):
    """Contrato completo de persistencia de dispositivos (lectura + escritura).

    Servicios que solo necesitan leer dependen de IDispositivoLector; los que
    solo escriben dependen de IDispositivoEscritor (segregación de interfaces).
    """
# endregion
