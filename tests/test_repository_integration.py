"""Pruebas de integración: DispositivoRepository + SQLAlchemy contra una base
de datos real (SQLite en memoria).

A diferencia de las pruebas unitarias con repositorio en memoria, estas
verifican que el mapeo ORM, las consultas y las restricciones de la base de
datos (como el número de serie único) funcionan correctamente en conjunto.
"""
# region Imports
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Dispositivo, EstadoDispositivo, TipoDispositivo
from src.repositories.dispositivo_repository import DispositivoRepository
from src.validation.dispositivo_validator import ValidationError
# endregion


# region Fixtures y utilidades
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()


@pytest.fixture
def repositorio(session):
    return DispositivoRepository(session)


def _dispositivo(**overrides):
    datos = dict(
        nombre="Laptop Dell", tipo=TipoDispositivo.LAPTOP, marca="Dell", modelo="Inspiron",
        numero_serie="SN-001", fecha_adquisicion=date.today(), estado=EstadoDispositivo.NUEVO,
        precio=Decimal("100.00"), ubicacion="Bogotá",
    )
    datos.update(overrides)
    return Dispositivo(**datos)
# endregion


# region Pruebas
def test_agregar_y_obtener_por_id(repositorio):
    creado = repositorio.agregar(_dispositivo())
    assert creado.id is not None

    encontrado = repositorio.obtener_por_id(creado.id)
    assert encontrado.numero_serie == "SN-001"


def test_numero_serie_duplicado_lanza_validation_error(repositorio):
    repositorio.agregar(_dispositivo(numero_serie="SN-DUP"))
    with pytest.raises(ValidationError):
        repositorio.agregar(_dispositivo(numero_serie="SN-DUP"))


def test_filtrar_por_rango_de_precio(repositorio):
    repositorio.agregar(_dispositivo(numero_serie="SN-1", precio=Decimal("50")))
    repositorio.agregar(_dispositivo(numero_serie="SN-2", precio=Decimal("500")))

    resultado = repositorio.filtrar(precio_min=Decimal("100"))

    assert [d.numero_serie for d in resultado] == ["SN-2"]


def test_buscar_por_nombre_ignora_mayusculas(repositorio):
    repositorio.agregar(_dispositivo(numero_serie="SN-1", nombre="Laptop Dell"))

    resultado = repositorio.buscar(nombre="dell")

    assert len(resultado) == 1


def test_eliminar_dispositivo(repositorio):
    creado = repositorio.agregar(_dispositivo())
    repositorio.eliminar(creado)
    assert repositorio.obtener_por_id(creado.id) is None
# endregion
