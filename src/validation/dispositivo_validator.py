"""Validación de datos de dispositivos."""
from __future__ import annotations

# region Imports
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal, InvalidOperation

from src.models import EstadoDispositivo, TipoDispositivo
# endregion


# region Excepciones
class ValidationError(Exception):
    """Error de validación de datos de entrada."""
# endregion


# region Contrato de regla de validación
class IReglaValidacion(ABC):
    """Contrato de una regla de validación individual.

    Nuevas reglas se implementan como una clase más; no requieren modificar
    ninguna clase existente (principio abierto/cerrado).
    """

    @abstractmethod
    def validar(self, datos: dict) -> None:
        """Lanza ValidationError si los datos no cumplen la regla."""
# endregion


# region Reglas concretas
class CamposObligatoriosRule(IReglaValidacion):
    _CAMPOS = ("nombre", "marca", "modelo", "numero_serie", "ubicacion")

    def validar(self, datos: dict) -> None:
        for campo in self._CAMPOS:
            valor = datos.get(campo)
            if not valor or not str(valor).strip():
                raise ValidationError(f"El campo '{campo}' es obligatorio.")


class TipoDispositivoValidoRule(IReglaValidacion):
    def validar(self, datos: dict) -> None:
        if not isinstance(datos.get("tipo"), TipoDispositivo):
            raise ValidationError(
                f"Tipo inválido. Opciones válidas: {[t.value for t in TipoDispositivo]}"
            )


class EstadoDispositivoValidoRule(IReglaValidacion):
    def validar(self, datos: dict) -> None:
        if not isinstance(datos.get("estado"), EstadoDispositivo):
            raise ValidationError(
                f"Estado inválido. Opciones válidas: {[e.value for e in EstadoDispositivo]}"
            )


class FechaAdquisicionValidaRule(IReglaValidacion):
    def validar(self, datos: dict) -> None:
        fecha = datos.get("fecha_adquisicion")
        if not isinstance(fecha, date):
            raise ValidationError("La fecha de adquisición no es válida.")
        if fecha > date.today():
            raise ValidationError("La fecha de adquisición no puede ser futura.")


class PrecioValidoRule(IReglaValidacion):
    def validar(self, datos: dict) -> None:
        try:
            precio = Decimal(str(datos.get("precio")))
        except (InvalidOperation, TypeError):
            raise ValidationError("El precio debe ser un valor numérico.")
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
# endregion


# region Validador compuesto
class DispositivoValidator:
    """Ejecuta un conjunto de reglas sobre los datos de un dispositivo."""

    _REGLAS_POR_DEFECTO = (
        CamposObligatoriosRule(),
        TipoDispositivoValidoRule(),
        EstadoDispositivoValidoRule(),
        FechaAdquisicionValidaRule(),
        PrecioValidoRule(),
    )

    # region Constructor
    def __init__(self, reglas: list[IReglaValidacion] | None = None):
        self._reglas = reglas or list(self._REGLAS_POR_DEFECTO)
    # endregion

    # region Validación
    def validar(self, datos: dict) -> None:
        for regla in self._reglas:
            regla.validar(datos)
    # endregion
# endregion
