# Generador de Contenido SEO para YouTube

Esta es una herramienta de línea de comandos diseñada para automatizar la creación de metadatos optimizados para videos de YouTube. El script procesa archivos de video, extrae su contenido de texto mediante OCR y utiliza el modelo de IA Gemini 2.0 Flash de Google para generar títulos, descripciones y etiquetas (tags) listos para publicar.

Además, gestiona un catálogo en formato Excel con una cola de publicación automática.

## Funcionalidades Principales

- **Procesamiento en Lote**: Procesa un único archivo de video o un directorio completo de forma recursiva.
- **Extracción por OCR**: Utiliza Tesseract-OCR para leer subtítulos incrustados (hardsubs) directamente de los fotogramas del video.
- **Generación con IA**: Se conecta a la API de Gemini 2.0 Flash para crear contenido SEO:
  - **Títulos**: Optimizados para búsquedas, con un hashtag y de menos de 100 caracteres.
  - **Descripciones**: Atractivas y detalladas, con 3-5 hashtags para mejorar la visibilidad.
  - **Tags (Etiquetas)**: Una lista de 15 a 24 palabras clave relevantes, separadas por comas, listas para pegar en YouTube.
- **Catálogo en Excel**: Guarda automáticamente toda la información generada en un archivo `catalogo_videos.xlsx`.
- **Programación Automática**: Calcula y asigna una fecha y hora de publicación para cada video, siguiendo un patrón de 6 videos diarios (6 AM, 8 AM, 10 AM, 12 PM, 2 PM, 4 PM).

## Requisitos Previos

Antes de ejecutar el script, asegúrate de tener lo siguiente:

1.  **Python 3.11+**.
2.  **Tesseract-OCR**: El motor de OCR debe estar instalado en tu sistema y accesible a través del PATH del sistema.
    - Puedes descargarlo desde la [wiki de Tesseract en GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
3.  **Clave de API de Google**: Necesitas una clave de API para el servicio de Gemini. Puedes obtenerla en [Google AI Studio](https://aistudio.google.com/app/apikey).

## Instalación y Configuración

1.  **Clona o descarga el proyecto** en tu máquina local.

2.  **Instala las dependencias**: Este proyecto usa `uv` para la gestión de paquetes. Abre una terminal en el directorio del proyecto y ejecuta:
    ```bash
    uv pip sync pyproject.toml
    ```

3.  **Crea el archivo de entorno**: En el directorio raíz del proyecto, crea un archivo llamado `.env`.

4.  **Configura tu API Key**: Abre el archivo `.env` y añade tu clave de API de Google de la siguiente manera:
    ```
    GOOGLE_API_KEY="TU_CLAVE_DE_API_AQUI"
    ```

## Modo de Uso

La herramienta se ejecuta desde la línea de comandos. Puedes pasarle la ruta a un solo archivo de video o a una carpeta que contenga múltiples videos.

-   **Para procesar un solo archivo de video:**
    ```bash
    uv run .\media-detailer.py "C:\ruta\completa\a\tu\video.mp4"
    ```

-   **Para procesar un directorio completo de forma recursiva:**
    ```bash
    uv run .\media-detailer.py "C:\ruta\completa\a\tu\carpeta_de_videos"
    ```

## Archivo de Salida: `catalogo_videos.xlsx`

El script creará o actualizará un archivo Excel con la siguiente estructura:

| ID Unico | Nombre del Archivo | Titulo | Descripcion | Hashtags (Tags) | Fecha de Catalogacion | Fecha de Programacion |
|---|---|---|---|---|---|---|
| ... | mi_video_01.mp4 | ... | ... | ... | ... | ... |
| ... | otro_video.mov | ... | ... | ... | ... | ... |

- **Hashtags (Tags)**: Esta columna contiene la lista de etiquetas separadas por comas, listas para ser pegadas en el campo "Etiquetas" de YouTube.