"""Punto de entrada: compone las dependencias y arranca la aplicación."""
# region Imports
import sys

from src.database import get_session, init_db
from src.repositories.dispositivo_repository import DispositivoRepository
from src.services.informe_service import InformeService
from src.services.inventario_service import InventarioService
from src.ui.console_ui import ConsoleUI
from src.validation.dispositivo_validator import DispositivoValidator
# endregion


# region Composición y arranque
def _configurar_consola_utf8() -> None:
    """En Windows, fuerza codepage UTF-8 (tildes/ñ) y habilita colores ANSI."""
    if sys.platform != "win32":
        return
    import ctypes

    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    STD_OUTPUT_HANDLE = -11
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    modo = ctypes.c_uint32()
    if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(modo)):
        ctypes.windll.kernel32.SetConsoleMode(
            handle, modo.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )


def main() -> None:
    _configurar_consola_utf8()
    init_db()
    session = get_session()
    try:
        repositorio = DispositivoRepository(session)
        validador = DispositivoValidator()
        inventario_service = InventarioService(repositorio, validador)
        informe_service = InformeService(repositorio)
        ConsoleUI(inventario_service, informe_service).run()
    finally:
        session.close()


if __name__ == "__main__":
    main()
# endregion
