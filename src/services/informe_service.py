"""Generación de informes del inventario."""
from __future__ import annotations

# region Imports
from decimal import Decimal

from src.repositories.base_repository import IDispositivoLector
# endregion


# region InformeService
class InformeService:
    """Depende únicamente de la capacidad de lectura del repositorio
    (segregación de interfaces): un informe nunca necesita escribir datos."""

    # region Constructor
    def __init__(self, lector: IDispositivoLector):
        self._lector = lector
    # endregion

    # region Informe
    def generar_informe(self) -> dict:
        dispositivos = self._lector.listar_todos()
        total = len(dispositivos)
        valor_total = sum((d.precio for d in dispositivos), Decimal("0"))
        valor_promedio = valor_total / total if total else Decimal("0")

        por_tipo: dict[str, int] = {}
        por_estado: dict[str, int] = {}
        for d in dispositivos:
            por_tipo[d.tipo.value] = por_tipo.get(d.tipo.value, 0) + 1
            por_estado[d.estado.value] = por_estado.get(d.estado.value, 0) + 1

        return {
            "total_dispositivos": total,
            "valor_total": valor_total,
            "valor_promedio": valor_promedio,
            "por_tipo": por_tipo,
            "por_estado": por_estado,
        }
    # endregion
# endregion
