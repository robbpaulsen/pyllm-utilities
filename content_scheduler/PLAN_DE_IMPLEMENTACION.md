# Plan de Implementación Detallado: Content Scheduler

Este documento describe el plan de desarrollo por fases para el proyecto `Content Scheduler`, basado en los lineamientos de `README.md` y `GEMINI.md` e incorporando las reglas de desarrollo especificadas.

---

## Reglas Generales de Desarrollo

1.  **Gestor de Entorno y Paquetes:** Se utilizará exclusivamente `uv` para la gestión del entorno virtual y las dependencias.
2.  **Gestión de Dependencias:** Toda librería se añadirá al `pyproject.toml` mediante el comando `uv add <libreria>`.
3.  **Calidad de Código:** Se utilizará `ruff` para el formateo y el linting del código. Se ejecutarán `ruff format .` y `ruff check .` regularmente.
4.  **Pruebas Unitarias:** Al final de cada fase de implementación, se desarrollará al menos una prueba unitaria utilizando `pytest` para validar el comportamiento del código añadido.

---

## Fase 0: Cimientos y Configuración del Proyecto

**Objetivo:** Establecer una base sólida, segura y estandarizada para el proyecto.

- **Tarea 0.1: Estructura del Proyecto y Dependencias**
  - [ ] Crear un directorio `src/content_scheduler` para el código fuente y `tests/` para las pruebas.
  - [ ] Mover los scripts `uploader.py` y `scheduler.py` a `src/content_scheduler/`.
  - [ ] Crear `__init__.py` en los directorios necesarios para definirlos como paquetes.
  - [ ] Activar el entorno virtual con `uv`.
  - [ ] Añadir dependencias de producción (`google-api-python-client`, `google-auth-oauthlib`, `pandas`) con `uv add`.
  - [ ] Añadir dependencias de desarrollo (`ruff`, `pytest`) con `uv add --dev`.

- **Tarea 0.2: Módulo de Autenticación (Reutilizable)**
  - [ ] Crear un script `src/content_scheduler/auth.py`.
  - [ ] Implementar la función `get_authenticated_service()` que maneje el flujo OAuth 2.0.
  - [ ] Asegurarse de que los secretos (`client_secrets.json`, `token.pickle`, etc.) estén en `.gitignore`.

- **Tarea 0.3: Módulo de Configuración**
  - [ ] Crear un script `src/content_scheduler/config.py`.
  - [ ] Definir variables para rutas (`pathlib.Path`), scopes de la API y valores por defecto.

- **Tarea 0.4: Configuración del Logging**
  - [ ] Crear un módulo `src/content_scheduler/logging_config.py`.
  - [ ] Configurar un logger que escriba en consola y en un archivo (`content_scheduler.log`).

- **Tarea 0.5: Pruebas de Configuración Inicial**
  - [ ] Crear una prueba simple en `tests/test_initial_setup.py` que importe los módulos creados para asegurar que la estructura del proyecto y las importaciones funcionen correctamente.
  - [ ] Ejecutar `pytest` para validar.

---

## Fase 1: Implementación del Uploader (`uploader.py`)

**Objetivo:** Desarrollar el script que sube los videos a YouTube en modo privado y recolecta sus IDs.

- **Tarea 1.1: Lógica Principal del Uploader**
  - [ ] Implementar la lógica para listar archivos de video de un directorio.
  - [ ] Iterar sobre cada archivo, llamando a la función de carga.

- **Tarea 1.2: Interacción con la API y Recolección de IDs**
  - [ ] Implementar la función que ejecuta la llamada `videos().insert()` con `status='private'`.
  - [ ] Capturar y almacenar los `video_id` retornados.
  - [ ] Guardar los IDs en un archivo CSV.

- **Tarea 1.3: Feedback, Errores y Calidad de Código**
  - [ ] Integrar el logger para informar el progreso y los errores.
  - [ ] Implementar `try...except` para manejar fallos en la carga de videos individuales.
  - [ ] Ejecutar `ruff format .` y `ruff check .` para limpiar el código.

- **Tarea 1.4: Pruebas Unitarias del Uploader**
  - [ ] Crear `tests/test_uploader.py`.
  - [ ] Escribir una prueba que simule (`mock`) la llamada a la API y verifique que la función de carga procesa la respuesta y extrae el ID correctamente.
  - [ ] Ejecutar `pytest` para validar.

---

## Fase 2: Implementación del Scheduler (`scheduler.py`)

**Objetivo:** Desarrollar el script que aplica los metadatos y programa los videos.

- **Tarea 2.1: Lógica Principal y Procesamiento de Datos**
  - [ ] Implementar la lectura del archivo de IDs y del archivo de metadatos con `pandas`.
  - [ ] Combinar los dos conjuntos de datos.

- **Tarea 2.2: Interacción con la API**
  - [ ] Iterar sobre los datos y construir el `body` para la solicitud `videos().update()`.
  - [ ] Implementar la lógica para transformar los datos (ej. `tags` de string a lista).
  - [ ] Ejecutar la llamada a la API.

- **Tarea 2.3: Feedback, Errores y Calidad de Código**
  - [ ] Integrar el logger para informar el progreso y los errores de la programación.
  - [ ] Ejecutar `ruff format .` y `ruff check .`.

- **Tarea 2.4: Pruebas Unitarias del Scheduler**
  - [ ] Crear `tests/test_scheduler.py`.
  - [ ] Escribir una prueba que verifique la correcta construcción del `body` de la API a partir de una fila de datos de ejemplo.
  - [ ] Ejecutar `pytest` para validar.

---

## Fase 3: Refinamiento y Usabilidad

**Objetivo:** Mejorar la robustez, flexibilidad y facilidad de uso de la herramienta.

- **Tarea 3.1: Argumentos por Línea de Comandos**
  - [ ] Integrar `argparse` para permitir especificar rutas y configuraciones al ejecutar los scripts.

- **Tarea 3.2: Manejo de Errores Avanzado**
  - [ ] Implementar reintentos con `exponential backoff` para la gestión de cuotas de la API.

- **Tarea 3.3: Documentación y Calidad de Código**
  - [ ] Añadir `docstrings` a todas las funciones y módulos.
  - [ ] Actualizar `README.md` con instrucciones de uso detalladas.
  - [ ] Ejecutar `ruff format .` y `ruff check .` en todo el proyecto.

- **Tarea 3.4: Pruebas de Integración**
  - [ ] Escribir una prueba en `tests/` que simule el flujo completo, verificando que los componentes (`auth`, `config`, `uploader`, `scheduler`) interactúan como se espera.
  - [ ] Ejecutar `pytest` para validar.
