"""Repositorio en memoria para pruebas unitarias de la capa de servicios.

Sustituye a DispositivoRepository sin tocar una base de datos real, gracias
a que ambos implementan el mismo contrato (IDispositivoRepository) y a la
inversión de dependencias aplicada en InventarioService/InformeService.
"""
from __future__ import annotations

# region Imports
from datetime import date
from decimal import Decimal

from src.models import Dispositivo, EstadoDispositivo, TipoDispositivo
from src.repositories.base_repository import IDispositivoRepository
from src.validation.dispositivo_validator import ValidationError
# endregion


# region FakeDispositivoRepository
class FakeDispositivoRepository(IDispositivoRepository):
    # region Constructor
    def __init__(self):
        self._dispositivos: dict[int, Dispositivo] = {}
        self._siguiente_id = 1
    # endregion

    # region Lectura
    def listar_todos(self) -> list[Dispositivo]:
        return sorted(self._dispositivos.values(), key=lambda d: d.id)

    def obtener_por_id(self, id_dispositivo: int) -> Dispositivo | None:
        return self._dispositivos.get(id_dispositivo)

    def buscar(
        self,
        nombre: str | None = None,
        marca: str | None = None,
        tipo: TipoDispositivo | None = None,
        estado: EstadoDispositivo | None = None,
    ) -> list[Dispositivo]:
        resultado = self.listar_todos()
        if nombre:
            resultado = [d for d in resultado if nombre.lower() in d.nombre.lower()]
        if marca:
            resultado = [d for d in resultado if marca.lower() in d.marca.lower()]
        if tipo:
            resultado = [d for d in resultado if d.tipo == tipo]
        if estado:
            resultado = [d for d in resultado if d.estado == estado]
        return resultado

    def filtrar(
        self,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
        ubicacion: str | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Dispositivo]:
        resultado = self.listar_todos()
        if precio_min is not None:
            resultado = [d for d in resultado if d.precio >= precio_min]
        if precio_max is not None:
            resultado = [d for d in resultado if d.precio <= precio_max]
        if ubicacion:
            resultado = [d for d in resultado if ubicacion.lower() in d.ubicacion.lower()]
        if fecha_desde is not None:
            resultado = [d for d in resultado if d.fecha_adquisicion >= fecha_desde]
        if fecha_hasta is not None:
            resultado = [d for d in resultado if d.fecha_adquisicion <= fecha_hasta]
        return resultado
    # endregion

    # region Escritura
    def agregar(self, dispositivo: Dispositivo) -> Dispositivo:
        for existente in self._dispositivos.values():
            if existente.numero_serie == dispositivo.numero_serie:
                raise ValidationError(
                    f"Ya existe un dispositivo con el número de serie "
                    f"'{dispositivo.numero_serie}'."
                )
        dispositivo.id = self._siguiente_id
        self._siguiente_id += 1
        self._dispositivos[dispositivo.id] = dispositivo
        return dispositivo

    def actualizar(self, dispositivo: Dispositivo) -> Dispositivo:
        self._dispositivos[dispositivo.id] = dispositivo
        return dispositivo

    def eliminar(self, dispositivo: Dispositivo) -> None:
        self._dispositivos.pop(dispositivo.id, None)
    # endregion
# endregion
