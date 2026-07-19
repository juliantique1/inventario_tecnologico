"""Lógica de negocio para la gestión del inventario."""
from __future__ import annotations

# region Imports
from decimal import Decimal

from src.models import Dispositivo, EstadoDispositivo, TipoDispositivo
from src.repositories.base_repository import IDispositivoRepository
from src.validation.dispositivo_validator import DispositivoValidator, ValidationError
# endregion


# region InventarioService
class InventarioService:
    """Casos de uso del inventario. Depende de la abstracción del repositorio,
    no de una implementación concreta (inversión de dependencias)."""

    # region Constructor
    def __init__(self, repositorio: IDispositivoRepository, validador: DispositivoValidator):
        self._repositorio = repositorio
        self._validador = validador
    # endregion

    # region Crear
    def crear_dispositivo(
        self,
        nombre: str,
        tipo: TipoDispositivo,
        marca: str,
        modelo: str,
        numero_serie: str,
        fecha_adquisicion,
        estado: EstadoDispositivo,
        precio: Decimal,
        ubicacion: str,
    ) -> Dispositivo:
        datos = dict(
            nombre=nombre, tipo=tipo, marca=marca, modelo=modelo,
            numero_serie=numero_serie, fecha_adquisicion=fecha_adquisicion,
            estado=estado, precio=precio, ubicacion=ubicacion,
        )
        self._validador.validar(datos)
        dispositivo = Dispositivo(
            nombre=nombre.strip(), tipo=tipo, marca=marca.strip(), modelo=modelo.strip(),
            numero_serie=numero_serie.strip(), fecha_adquisicion=fecha_adquisicion,
            estado=estado, precio=Decimal(str(precio)), ubicacion=ubicacion.strip(),
        )
        return self._repositorio.agregar(dispositivo)
    # endregion

    # region Consultar
    def listar_dispositivos(self) -> list[Dispositivo]:
        return self._repositorio.listar_todos()

    def obtener_dispositivo(self, id_dispositivo: int) -> Dispositivo | None:
        return self._repositorio.obtener_por_id(id_dispositivo)

    def buscar_dispositivos(self, **criterios) -> list[Dispositivo]:
        return self._repositorio.buscar(**criterios)

    def filtrar_avanzado(self, **criterios) -> list[Dispositivo]:
        return self._repositorio.filtrar(**criterios)
    # endregion

    # region Actualizar
    def actualizar_dispositivo(self, id_dispositivo: int, **campos) -> Dispositivo:
        dispositivo = self._repositorio.obtener_por_id(id_dispositivo)
        if dispositivo is None:
            raise ValidationError(f"No existe un dispositivo con id {id_dispositivo}.")

        datos = self._datos_actuales(dispositivo)
        datos.update({k: v for k, v in campos.items() if v is not None})
        self._validador.validar(datos)

        for campo, valor in datos.items():
            setattr(dispositivo, campo, valor)

        return self._repositorio.actualizar(dispositivo)
    # endregion

    # region Eliminar
    def eliminar_dispositivo(self, id_dispositivo: int) -> bool:
        dispositivo = self._repositorio.obtener_por_id(id_dispositivo)
        if dispositivo is None:
            return False
        self._repositorio.eliminar(dispositivo)
        return True
    # endregion

    # region Utilidades privadas
    @staticmethod
    def _datos_actuales(dispositivo: Dispositivo) -> dict:
        return dict(
            nombre=dispositivo.nombre, tipo=dispositivo.tipo, marca=dispositivo.marca,
            modelo=dispositivo.modelo, numero_serie=dispositivo.numero_serie,
            fecha_adquisicion=dispositivo.fecha_adquisicion, estado=dispositivo.estado,
            precio=dispositivo.precio, ubicacion=dispositivo.ubicacion,
        )
    # endregion
# endregion
