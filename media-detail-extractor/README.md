# Generador de Contenido SEO para YouTube con IA Multimodal

Esta es una herramienta de línea de comandos diseñada para automatizar la creación de metadatos optimizados para videos de YouTube. El script procesa archivos de video, **analiza su contenido visual y contextual usando el modelo de IA multimodal Gemini 2.0 Flash de Google**, y genera títulos, descripciones y etiquetas (tags) listos para publicar.

Además, gestiona un catálogo en formato Excel con una cola de publicación automática.

## Funcionalidades Principales

- **Procesamiento en Lote**: Procesa un único archivo de video o un directorio completo de forma recursiva.
- **Análisis Multimodal con IA**: Utiliza el modelo Gemini 2.0 Flash para analizar el contenido completo del video (imágenes, contexto, etc.), no solo texto.
- **Generación de Contenido SEO**: Se conecta a la API de Gemini para crear:
  - **Títulos**: Optimizados para búsquedas, con un hashtag y de menos de 100 caracteres.
  - **Descripciones**: Atractivas y detalladas, con 3-5 hashtags para mejorar la visibilidad.
  - **Tags (Etiquetas)**: Una lista de 15 a 24 palabras clave relevantes, separadas por comas, listas para pegar en YouTube.
- **Catálogo en Excel**: Guarda automáticamente toda la información generada en un archivo `catalogo_videos.xlsx`.
- **Programación Automática**: Calcula y asigna una fecha y hora de publicación para cada video, siguiendo un patrón de 6 videos diarios (6 AM, 8 AM, 10 AM, 12 PM, 2 PM, 4 PM).

## Requisitos Previos

Antes de ejecutar el script, asegúrate de tener lo siguiente:

1.  **Python 3.11+**.
2.  **uv**: Un instalador y gestor de paquetes de Python rápido. Puedes instalarlo desde [su sitio web oficial](https://github.com/astral-sh/uv).
3.  **Clave de API de Google**: Necesitas una clave de API para el servicio de Gemini. Puedes obtenerla en [Google AI Studio](https://aistudio.google.com/app/apikey).

## Instalación y Configuración

1.  **Clona o descarga el proyecto** en tu máquina local.

2.  **Crea un entorno virtual e instala las dependencias**: Este proyecto usa `uv`. Abre una terminal en el directorio del proyecto y ejecuta:
    ```bash
    # Crea un entorno virtual en la carpeta .venv
    uv venv

    # Activa el entorno virtual (en Windows)
    .venv\Scripts\activate

    # Instala las dependencias del pyproject.toml
    uv pip sync pyproject.toml
    ```

3.  **Crea el archivo de entorno**: En el directorio raíz del proyecto, crea un archivo llamado `.env`.

4.  **Configura tu API Key**: Abre el archivo `.env` y añade tu clave de API de Google de la siguiente manera:
    ```
    GOOGLE_API_KEY="TU_CLAVE_DE_API_AQUI"
    ```

## Modo de Uso

La herramienta se ejecuta desde la línea de comandos, dentro del entorno virtual activado.

-   **Para procesar un solo archivo de video:**
    ```bash
    python media-detailer.py "C:\ruta\completa\a\tu\video.mp4"
    ```

-   **Para procesar un directorio completo de forma recursiva:**
    ```bash
    python media-detailer.py "./videos"
    ```
    (Donde `./videos` es una carpeta en el directorio del proyecto).

## Archivo de Salida: `catalogo_videos.xlsx`

El script creará o actualizará un archivo Excel con la siguiente estructura:

| ID Unico | Nombre del Archivo | Titulo | Descripcion | Hashtags | Fecha de Catalogacion | Fecha de Programacion |
|---|---|---|---|---|---|---|
| ... | mi_video_01.mp4 | ... | ... | ... | ... | ... |
| ... | otro_video.mov | ... | ... | ... | ... | ... |

- **Hashtags**: Esta columna contiene la lista de etiquetas separadas por comas, listas para ser pegadas en el campo "Etiquetas" de YouTube.
