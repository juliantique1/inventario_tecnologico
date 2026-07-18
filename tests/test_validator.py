"""Pruebas unitarias de DispositivoValidator (verificación de requisitos)."""
# region Imports
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.models import EstadoDispositivo, TipoDispositivo
from src.validation.dispositivo_validator import DispositivoValidator, ValidationError
# endregion


# region Utilidades
def _datos_validos(**overrides):
    datos = dict(
        nombre="Laptop Dell", tipo=TipoDispositivo.LAPTOP, marca="Dell", modelo="Inspiron",
        numero_serie="SN-001", fecha_adquisicion=date.today(), estado=EstadoDispositivo.NUEVO,
        precio=Decimal("100.00"), ubicacion="Bogotá",
    )
    datos.update(overrides)
    return datos
# endregion


# region Pruebas
class TestDispositivoValidator:
    def setup_method(self):
        self.validador = DispositivoValidator()

    def test_datos_validos_no_lanza_error(self):
        self.validador.validar(_datos_validos())

    @pytest.mark.parametrize("campo", ["nombre", "marca", "modelo", "numero_serie", "ubicacion"])
    def test_campo_obligatorio_vacio_lanza_error(self, campo):
        with pytest.raises(ValidationError):
            self.validador.validar(_datos_validos(**{campo: "   "}))

    def test_tipo_invalido_lanza_error(self):
        with pytest.raises(ValidationError):
            self.validador.validar(_datos_validos(tipo="Laptop"))

    def test_estado_invalido_lanza_error(self):
        with pytest.raises(ValidationError):
            self.validador.validar(_datos_validos(estado="Nuevo"))

    def test_fecha_futura_lanza_error(self):
        futura = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError):
            self.validador.validar(_datos_validos(fecha_adquisicion=futura))

    def test_fecha_hoy_es_valida(self):
        self.validador.validar(_datos_validos(fecha_adquisicion=date.today()))

    def test_precio_negativo_lanza_error(self):
        with pytest.raises(ValidationError):
            self.validador.validar(_datos_validos(precio=Decimal("-1")))

    def test_precio_no_numerico_lanza_error(self):
        with pytest.raises(ValidationError):
            self.validador.validar(_datos_validos(precio="gratis"))
# endregion
