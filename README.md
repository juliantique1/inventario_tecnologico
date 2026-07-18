# Inventario Tecnológico - TecnoSoluciones

Sistema de gestión de inventario de equipos tecnológicos desarrollado en Python, con MySQL como motor de base de datos y SQLAlchemy como ORM. Aplicación de consola que permite administrar el inventario de dispositivos de la empresa TecnoSoluciones.

## Estructura del proyecto

```
inventario_tecnologico/
├── src/
│   ├── __init__.py
│   ├── models.py                              # Entidades del dominio (Dispositivo, Enums)
│   ├── database.py                             # Configuración de conexión a la base de datos
│   ├── validation/
│   │   └── dispositivo_validator.py            # Reglas de validación de datos
│   ├── repositories/
│   │   ├── base_repository.py                  # Interfaces de persistencia (contratos)
│   │   └── dispositivo_repository.py           # Implementación con SQLAlchemy
│   ├── services/
│   │   ├── inventario_service.py               # Casos de uso CRUD
│   │   └── informe_service.py                  # Generación de informes
│   └── ui/
│       └── console_ui.py                        # Interfaz de consola
├── main.py                                       # Punto de entrada (composition root)
├── requirements.txt                              # Dependencias del proyecto
├── .env.example                                   # Plantilla de variables de entorno
└── README.md
```

Cada archivo está organizado internamente con bloques `# region ... # endregion` (a nivel de módulo y, dentro de las clases, a nivel de sección: constructor, lectura, escritura, utilidades privadas, etc.), de forma jerárquica y plegable en editores como VS Code o PyCharm.

## Arquitectura y principios SOLID

El proyecto separa responsabilidades en capas, donde cada una depende de abstracciones y no de implementaciones concretas:

```
ConsoleUI  →  InventarioService / InformeService  →  IDispositivoRepository  →  DispositivoRepository (SQLAlchemy)
                          ↓
                  DispositivoValidator
```

- **S — Single Responsibility**: cada clase tiene una única razón para cambiar. `models.py` solo define la entidad, `database.py` solo configura la conexión, `DispositivoValidator` solo valida, `DispositivoRepository` solo persiste, `InventarioService`/`InformeService` solo orquestan casos de uso, y `ConsoleUI` solo maneja entrada/salida por consola.
- **O — Open/Closed**: `DispositivoValidator` ejecuta una lista de reglas (`IReglaValidacion`). Para agregar una nueva validación se crea una clase de regla nueva y se añade a la lista; no se modifica el validador existente.
- **L — Liskov Substitution**: `DispositivoRepository` implementa íntegramente el contrato `IDispositivoRepository`, por lo que puede sustituirse en cualquier lugar por otra implementación (por ejemplo, un repositorio en memoria para pruebas) sin romper a quien lo consume.
- **I — Interface Segregation**: `base_repository.py` separa `IDispositivoLector` (lectura) de `IDispositivoEscritor` (escritura). `InformeService` depende únicamente de `IDispositivoLector`, porque generar un informe nunca requiere escribir datos.
- **D — Dependency Inversion**: `InventarioService` e `InformeService` reciben sus dependencias (repositorio, validador) por constructor y solo conocen las interfaces (`IDispositivoRepository`, `IDispositivoLector`), no la clase concreta de SQLAlchemy. `main.py` actúa como *composition root*: construye las implementaciones concretas y las inyecta.

## Requisitos

- Python 3.8+
- MySQL Server en ejecución
- pip

## Instalación

1. Clonar el repositorio y ubicarse en la carpeta del proyecto.

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Crear la base de datos en MySQL:

   ```sql
   CREATE DATABASE inventario_tecnologico CHARACTER SET utf8mb4;
   ```

5. Copiar `.env.example` a `.env` y ajustar las credenciales de conexión:

   ```bash
   copy .env.example .env
   ```

   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=tu_password
   DB_NAME=inventario_tecnologico
   ```

## Ejecución

```bash
python main.py
```

Al iniciar, `main.py` crea la tabla `dispositivos` si no existe (`init_db()`), compone las dependencias (repositorio, validador, servicios) y arranca el menú interactivo de consola.

## Modelo de datos

Tabla `dispositivos`:

| Campo               | Tipo               | Descripción                                   |
|---------------------|---------------------|-----------------------------------------------|
| id                  | Integer (PK)         | Identificador autoincremental                  |
| nombre              | String(100)          | Nombre del dispositivo                         |
| tipo                | Enum                 | Laptop, Smartphone, Tablet, Desktop, Monitor, Impresora, Otro |
| marca               | String(50)           | Marca del dispositivo                          |
| modelo              | String(50)           | Modelo del dispositivo                         |
| numero_serie        | String(100), único   | Número de serie                                |
| fecha_adquisicion   | Date                  | Fecha de adquisición                           |
| estado              | Enum                 | Nuevo, Usado, En reparación, Dado de baja      |
| precio              | Numeric(10,2)         | Precio del dispositivo                         |
| ubicacion           | String(100)           | Ubicación física del dispositivo               |

## Funcionalidades

- **CRUD completo**: agregar, listar, actualizar y eliminar dispositivos.
- **Búsqueda**: por nombre, marca, tipo y estado (criterios combinables).
- **Filtrado avanzado**: por rango de precio, ubicación y rango de fecha de adquisición.
- **Informes**: total de dispositivos, valor total y promedio del inventario, desglose por tipo y por estado.
- **Validaciones**: campos obligatorios, tipos y estados restringidos a valores válidos, fechas no futuras, precios no negativos y número de serie único (validado en código y a nivel de base de datos).

## Notas técnicas

- Las validaciones lanzan `ValidationError` (`src/validation/dispositivo_validator.py`), capturada en `ConsoleUI` para mostrar mensajes claros sin detener la aplicación.
- Los errores de integridad de MySQL (por ejemplo, número de serie duplicado) se capturan con `IntegrityError` de SQLAlchemy en `DispositivoRepository` y se traducen a `ValidationError`.
