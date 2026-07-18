"""Pruebas unitarias de InformeService."""
# region Imports
from datetime import date
from decimal import Decimal

import pytest

from src.models import EstadoDispositivo, TipoDispositivo
from src.services.informe_service import InformeService
from src.services.inventario_service import InventarioService
from src.validation.dispositivo_validator import DispositivoValidator
from tests.fakes import FakeDispositivoRepository
# endregion


# region Fixtures
@pytest.fixture
def repositorio():
    return FakeDispositivoRepository()


@pytest.fixture
def inventario(repositorio):
    return InventarioService(repositorio, DispositivoValidator())
# endregion


# region Pruebas
def test_informe_con_inventario_vacio(repositorio):
    informe = InformeService(repositorio).generar_informe()
    assert informe["total_dispositivos"] == 0
    assert informe["valor_promedio"] == Decimal("0")


def test_informe_calcula_totales_y_desgloses(inventario, repositorio):
    inventario.crear_dispositivo(
        nombre="Laptop", tipo=TipoDispositivo.LAPTOP, marca="Dell", modelo="X",
        numero_serie="SN-1", fecha_adquisicion=date.today(), estado=EstadoDispositivo.NUEVO,
        precio=Decimal("100"), ubicacion="Bogotá",
    )
    inventario.crear_dispositivo(
        nombre="Monitor", tipo=TipoDispositivo.MONITOR, marca="LG", modelo="Y",
        numero_serie="SN-2", fecha_adquisicion=date.today(), estado=EstadoDispositivo.USADO,
        precio=Decimal("50"), ubicacion="Bogotá",
    )

    informe = InformeService(repositorio).generar_informe()

    assert informe["total_dispositivos"] == 2
    assert informe["valor_total"] == Decimal("150")
    assert informe["valor_promedio"] == Decimal("75")
    assert informe["por_tipo"] == {"Laptop": 1, "Monitor": 1}
    assert informe["por_estado"] == {"Nuevo": 1, "Usado": 1}
# endregion
