"""Pruebas unitarias de InventarioService, usando un repositorio en memoria."""
# region Imports
from datetime import date
from decimal import Decimal

import pytest

from src.models import EstadoDispositivo, TipoDispositivo
from src.services.inventario_service import InventarioService
from src.validation.dispositivo_validator import DispositivoValidator, ValidationError
from tests.fakes import FakeDispositivoRepository
# endregion


# region Fixtures y utilidades
@pytest.fixture
def service():
    return InventarioService(FakeDispositivoRepository(), DispositivoValidator())


def _crear(service, numero_serie="SN-001", **overrides):
    datos = dict(
        nombre="Laptop Dell", tipo=TipoDispositivo.LAPTOP, marca="Dell", modelo="Inspiron",
        numero_serie=numero_serie, fecha_adquisicion=date.today(), estado=EstadoDispositivo.NUEVO,
        precio=Decimal("100.00"), ubicacion="Bogotá",
    )
    datos.update(overrides)
    return service.crear_dispositivo(**datos)
# endregion


# region Crear
class TestCrear:
    def test_crea_dispositivo_con_datos_validos(self, service):
        dispositivo = _crear(service)
        assert dispositivo.id == 1
        assert dispositivo.nombre == "Laptop Dell"

    def test_numero_serie_duplicado_lanza_error(self, service):
        _crear(service, numero_serie="SN-DUP")
        with pytest.raises(ValidationError):
            _crear(service, numero_serie="SN-DUP")

    def test_datos_invalidos_no_se_guardan(self, service):
        with pytest.raises(ValidationError):
            _crear(service, precio=Decimal("-5"))
        assert service.listar_dispositivos() == []
# endregion


# region Consultar
class TestConsultar:
    def test_listar_devuelve_todos(self, service):
        _crear(service, numero_serie="SN-1")
        _crear(service, numero_serie="SN-2")
        assert len(service.listar_dispositivos()) == 2

    def test_buscar_por_nombre_ignora_mayusculas(self, service):
        _crear(service, numero_serie="SN-1", nombre="Laptop Dell")
        _crear(service, numero_serie="SN-2", nombre="Monitor LG")
        resultado = service.buscar_dispositivos(nombre="dell")
        assert [d.numero_serie for d in resultado] == ["SN-1"]

    def test_filtrar_por_rango_de_precio(self, service):
        _crear(service, numero_serie="SN-1", precio=Decimal("50"))
        _crear(service, numero_serie="SN-2", precio=Decimal("500"))
        resultado = service.filtrar_avanzado(precio_min=Decimal("100"))
        assert [d.numero_serie for d in resultado] == ["SN-2"]
# endregion


# region Actualizar
class TestActualizar:
    def test_actualiza_campos_indicados_y_conserva_el_resto(self, service):
        dispositivo = _crear(service)
        actualizado = service.actualizar_dispositivo(dispositivo.id, precio=Decimal("200"))
        assert actualizado.precio == Decimal("200")
        assert actualizado.nombre == "Laptop Dell"

    def test_actualizar_id_inexistente_lanza_error(self, service):
        with pytest.raises(ValidationError):
            service.actualizar_dispositivo(999, precio=Decimal("10"))
# endregion


# region Eliminar
class TestEliminar:
    def test_elimina_dispositivo_existente(self, service):
        dispositivo = _crear(service)
        assert service.eliminar_dispositivo(dispositivo.id) is True
        assert service.listar_dispositivos() == []

    def test_eliminar_id_inexistente_devuelve_false(self, service):
        assert service.eliminar_dispositivo(999) is False
# endregion
