"""Pruebas del flujo de eliminación en ConsoleUI, simulando teclado y consola."""
# region Imports
from datetime import date
from decimal import Decimal

from src.models import EstadoDispositivo, TipoDispositivo
from src.services.informe_service import InformeService
from src.services.inventario_service import InventarioService
from src.ui.console_ui import ConsoleUI
from src.validation.dispositivo_validator import DispositivoValidator
from tests.fakes import FakeDispositivoRepository
# endregion


# region Utilidades
def _armar_ui():
    repositorio = FakeDispositivoRepository()
    inventario = InventarioService(repositorio, DispositivoValidator())
    informe = InformeService(repositorio)
    dispositivo = inventario.crear_dispositivo(
        nombre="Laptop Dell", tipo=TipoDispositivo.LAPTOP, marca="Dell", modelo="Inspiron",
        numero_serie="SN-001", fecha_adquisicion=date.today(), estado=EstadoDispositivo.NUEVO,
        precio=Decimal("100.00"), ubicacion="Bogotá",
    )
    return inventario, ConsoleUI(inventario, informe), dispositivo


def _ejecutar(ui, monkeypatch, respuestas):
    entradas = iter(respuestas)

    def fake_input(prompt=""):
        print(prompt, end="")
        return next(entradas)

    monkeypatch.setattr("builtins.input", fake_input)
    ui.run()
# endregion


# region Pruebas
def test_muestra_detalle_y_cancela_sin_eliminar(monkeypatch, capsys):
    inventario, ui, dispositivo = _armar_ui()

    _ejecutar(ui, monkeypatch, ["6", str(dispositivo.id), "n", "", "0"])

    salida = capsys.readouterr().out
    assert "Laptop Dell" in salida
    assert "¿Confirmas la eliminación de este dispositivo?" in salida
    assert inventario.obtener_dispositivo(dispositivo.id) is not None


def test_confirma_y_elimina(monkeypatch, capsys):
    inventario, ui, dispositivo = _armar_ui()

    _ejecutar(ui, monkeypatch, ["6", str(dispositivo.id), "s", "", "0"])

    salida = capsys.readouterr().out
    assert "Dispositivo eliminado." in salida
    assert inventario.obtener_dispositivo(dispositivo.id) is None


def test_id_inexistente_no_pide_confirmacion(monkeypatch, capsys):
    inventario, ui, _ = _armar_ui()

    _ejecutar(ui, monkeypatch, ["6", "999", "", "0"])

    salida = capsys.readouterr().out
    assert "No existe un dispositivo con ese id." in salida
# endregion
