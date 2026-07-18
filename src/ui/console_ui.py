"""Interfaz de consola del sistema de inventario tecnológico."""
# region Imports
from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.models import EstadoDispositivo, TipoDispositivo
from src.services.informe_service import InformeService
from src.services.inventario_service import InventarioService
from src.validation.dispositivo_validator import ValidationError
# endregion


# region Estilos de consola
_ROJO_NEGRITA = "\033[1;91m"
_RESET = "\033[0m"
# endregion


# region ConsoleUI
class ConsoleUI:
    """Encapsula toda la entrada/salida por consola; no conoce detalles de persistencia."""

    _MENU = """
==== Inventario Tecnológico - TecnoSoluciones ====
1. Agregar dispositivo
2. Listar todos los dispositivos
3. Buscar dispositivos
4. Filtrado avanzado
5. Actualizar dispositivo
6. Eliminar dispositivo
7. Generar informe
0. Salir
"""

    # region Constructor
    def __init__(self, inventario_service: InventarioService, informe_service: InformeService):
        self._inventario = inventario_service
        self._informes = informe_service
        self._acciones = {
            "1": self._agregar_dispositivo,
            "2": self._listar_dispositivos,
            "3": self._buscar_dispositivos,
            "4": self._filtrar_avanzado,
            "5": self._actualizar_dispositivo,
            "6": self._eliminar_dispositivo,
            "7": self._mostrar_informe,
        }
    # endregion

    # region Bucle principal
    def run(self) -> None:
        while True:
            print(self._MENU)
            opcion = input("Selecciona una opción: ").strip()
            if opcion == "0":
                print("¡Hasta luego!")
                break
            accion = self._acciones.get(opcion)
            if accion is None:
                print("Opción inválida.")
                continue
            accion()
            input("\nPresiona ENTER para volver al menú principal...")
    # endregion

    # region Acciones del menú
    def _agregar_dispositivo(self) -> None:
        print("\n--- Agregar nuevo dispositivo ---")
        nombre = self._leer_texto("Nombre del dispositivo: ")
        tipo = self._leer_opcion("Selecciona el tipo (número): ", TipoDispositivo)
        marca = self._leer_texto("Marca: ")
        modelo = self._leer_texto("Modelo: ")
        numero_serie = self._leer_texto("Número de serie: ")
        fecha_adquisicion = self._leer_fecha("Fecha de adquisición (AAAA-MM-DD): ", no_futura=True)
        estado = self._leer_opcion("Selecciona el estado (número): ", EstadoDispositivo)
        precio = self._leer_decimal("Precio: ")
        ubicacion = self._leer_texto("Ubicación: ")

        try:
            dispositivo = self._inventario.crear_dispositivo(
                nombre, tipo, marca, modelo, numero_serie,
                fecha_adquisicion, estado, precio, ubicacion,
            )
            print(f"Dispositivo creado con id {dispositivo.id}.")
        except ValidationError as e:
            self._imprimir_error(str(e))

    def _listar_dispositivos(self) -> None:
        print("\n--- Listado de dispositivos ---")
        self._imprimir_lista(self._inventario.listar_dispositivos())

    def _buscar_dispositivos(self) -> None:
        print("\n--- Buscar dispositivos ---")
        print("Deja en blanco los criterios que no quieras usar.")
        nombre = self._leer_texto("Nombre contiene: ", permitir_vacio=True)
        marca = self._leer_texto("Marca contiene: ", permitir_vacio=True)

        tipo = None
        if input("¿Filtrar por tipo? (s/n): ").strip().lower() == "s":
            tipo = self._leer_opcion("Selecciona el tipo (número): ", TipoDispositivo)

        estado = None
        if input("¿Filtrar por estado? (s/n): ").strip().lower() == "s":
            estado = self._leer_opcion("Selecciona el estado (número): ", EstadoDispositivo)

        resultados = self._inventario.buscar_dispositivos(
            marca=marca or None, tipo=tipo, estado=estado, nombre=nombre or None
        )
        self._imprimir_lista(resultados)

    def _filtrar_avanzado(self) -> None:
        print("\n--- Filtrado avanzado ---")
        print("Deja en blanco los criterios que no quieras usar.")
        precio_min = self._leer_decimal("Precio mínimo: ", permitir_vacio=True)
        precio_max = self._leer_decimal("Precio máximo: ", permitir_vacio=True)
        ubicacion = self._leer_texto("Ubicación contiene: ", permitir_vacio=True)
        fecha_desde = self._leer_fecha("Fecha adquisición desde (AAAA-MM-DD): ", permitir_vacio=True)
        fecha_hasta = self._leer_fecha("Fecha adquisición hasta (AAAA-MM-DD): ", permitir_vacio=True)

        resultados = self._inventario.filtrar_avanzado(
            precio_min=precio_min,
            precio_max=precio_max,
            ubicacion=ubicacion or None,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
        self._imprimir_lista(resultados)

    def _actualizar_dispositivo(self) -> None:
        print("\n--- Actualizar dispositivo ---")
        id_texto = self._leer_texto("Id del dispositivo a actualizar: ")
        if not id_texto.isdigit():
            print("Id inválido.")
            return
        dispositivo = self._inventario.obtener_dispositivo(int(id_texto))
        if dispositivo is None:
            print("No existe un dispositivo con ese id.")
            return

        self._imprimir_dispositivo(dispositivo)
        print("Presiona ENTER para conservar el valor actual de cada campo.")

        nombre = self._leer_texto(f"Nombre [{dispositivo.nombre}]: ", permitir_vacio=True)
        marca = self._leer_texto(f"Marca [{dispositivo.marca}]: ", permitir_vacio=True)
        modelo = self._leer_texto(f"Modelo [{dispositivo.modelo}]: ", permitir_vacio=True)
        numero_serie = self._leer_texto(
            f"Número de serie [{dispositivo.numero_serie}]: ", permitir_vacio=True
        )
        ubicacion = self._leer_texto(f"Ubicación [{dispositivo.ubicacion}]: ", permitir_vacio=True)

        tipo = None
        if input("¿Cambiar tipo? (s/n): ").strip().lower() == "s":
            tipo = self._leer_opcion("Selecciona el nuevo tipo (número): ", TipoDispositivo)

        estado = None
        if input("¿Cambiar estado? (s/n): ").strip().lower() == "s":
            estado = self._leer_opcion("Selecciona el nuevo estado (número): ", EstadoDispositivo)

        fecha_adquisicion = self._leer_fecha(
            "Nueva fecha de adquisición (AAAA-MM-DD), en blanco para conservar: ",
            permitir_vacio=True,
            no_futura=True,
        )
        precio = self._leer_decimal("Nuevo precio, en blanco para conservar: ", permitir_vacio=True)

        try:
            self._inventario.actualizar_dispositivo(
                dispositivo.id,
                nombre=nombre or None,
                tipo=tipo,
                marca=marca or None,
                modelo=modelo or None,
                numero_serie=numero_serie or None,
                fecha_adquisicion=fecha_adquisicion,
                estado=estado,
                precio=precio,
                ubicacion=ubicacion or None,
            )
            print("Dispositivo actualizado correctamente.")
        except ValidationError as e:
            self._imprimir_error(str(e))

    def _eliminar_dispositivo(self) -> None:
        print("\n--- Eliminar dispositivo ---")
        id_texto = self._leer_texto("Id del dispositivo a eliminar: ")
        if not id_texto.isdigit():
            print("Id inválido.")
            return

        dispositivo = self._inventario.obtener_dispositivo(int(id_texto))
        if dispositivo is None:
            print("No existe un dispositivo con ese id.")
            return

        self._imprimir_dispositivo(dispositivo)
        confirmacion = input("¿Confirmas la eliminación de este dispositivo? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("Operación cancelada.")
            return

        self._inventario.eliminar_dispositivo(dispositivo.id)
        print("Dispositivo eliminado.")

    def _mostrar_informe(self) -> None:
        print("\n--- Informe del inventario ---")
        informe = self._informes.generar_informe()
        print(f"Total de dispositivos: {informe['total_dispositivos']}")
        print(f"Valor total del inventario: {informe['valor_total']:.2f}")
        print(f"Valor promedio por dispositivo: {informe['valor_promedio']:.2f}")
        print("Dispositivos por tipo:")
        for tipo, cantidad in informe["por_tipo"].items():
            print(f"  {tipo}: {cantidad}")
        print("Dispositivos por estado:")
        for estado, cantidad in informe["por_estado"].items():
            print(f"  {estado}: {cantidad}")
    # endregion

    # region Entrada de datos
    def _leer_opcion(self, texto, opciones):
        lista = list(opciones)
        for i, op in enumerate(lista, start=1):
            print(f"  {i}. {op.value}")
        while True:
            entrada = input(texto).strip()
            if entrada.isdigit() and 1 <= int(entrada) <= len(lista):
                return lista[int(entrada) - 1]
            print("Opción inválida, intenta de nuevo.")

    def _leer_fecha(self, texto, permitir_vacio=False, no_futura=False):
        while True:
            entrada = input(texto).strip()
            if permitir_vacio and not entrada:
                return None
            try:
                fecha = datetime.strptime(entrada, "%Y-%m-%d").date()
            except ValueError:
                print("Formato de fecha inválido. Usa AAAA-MM-DD.")
                continue
            if no_futura and fecha > datetime.now().date():
                print(f"{_ROJO_NEGRITA}La fecha no puede ser futura.{_RESET}")
                continue
            return fecha

    def _leer_decimal(self, texto, permitir_vacio=False):
        while True:
            entrada = input(texto).strip()
            if permitir_vacio and not entrada:
                return None
            try:
                return Decimal(entrada)
            except InvalidOperation:
                print("Debes ingresar un número válido.")

    def _leer_texto(self, texto, permitir_vacio=False):
        while True:
            entrada = input(texto).strip()
            if entrada or permitir_vacio:
                return entrada
            print("Este campo es obligatorio.")
    # endregion

    # region Salida por consola
    def _imprimir_error(self, mensaje: str) -> None:
        print(f"{_ROJO_NEGRITA}>>> ERROR: {mensaje}{_RESET}")

    def _imprimir_dispositivo(self, d) -> None:
        print(
            f"  [{d.id}] {d.nombre} | {d.tipo.value} | {d.marca} {d.modelo} | "
            f"S/N: {d.numero_serie} | Adquirido: {d.fecha_adquisicion} | "
            f"Estado: {d.estado.value} | Precio: {d.precio:.2f} | Ubicación: {d.ubicacion}"
        )

    def _imprimir_lista(self, dispositivos) -> None:
        if not dispositivos:
            print("No se encontraron dispositivos.")
            return

        columnas = [
            "#", "ID", "Nombre", "Tipo", "Marca", "Modelo",
            "S/N", "Adquirido", "Estado", "Precio", "Ubicación",
        ]
        filas = [
            [
                str(i), str(d.id), d.nombre, d.tipo.value, d.marca, d.modelo,
                d.numero_serie, str(d.fecha_adquisicion), d.estado.value,
                f"{d.precio:.2f}", d.ubicacion,
            ]
            for i, d in enumerate(dispositivos, start=1)
        ]
        anchos = [
            max(len(columnas[i]), max(len(fila[i]) for fila in filas))
            for i in range(len(columnas))
        ]

        def formatear_fila(valores):
            return " | ".join(valor.ljust(anchos[i]) for i, valor in enumerate(valores))

        print(formatear_fila(columnas))
        print("-+-".join("-" * ancho for ancho in anchos))
        for fila in filas:
            print(formatear_fila(fila))
        print(f"Total: {len(dispositivos)} dispositivo(s).")
    # endregion
# endregion
