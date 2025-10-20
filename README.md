# Pyllm Utilities

> [!NOTE]
>
> Se pronuncia:
> _Paeei~yyllmm_
>

Es un set de utilidades que integran grandes modelos de lenguaje como palanca u apoyo para 
realizar tareas cotidianas. Al menos cotidianas para mi.

## Image Generation

Utilidad que integra la api gratuita de [Together AI](https://together.ai),
esta API permite a usuarios registrados en la plataoforma usar el modelo
[FLUX.1\[schnell\]](https://www.together.ai/models/flux-1-schnell) para generar
imagenes de un tamaxo maximo de 1024x1024 en base a un prompt de texto, tiene 
un RLM (Rate Limit) de 6 imagenes maximo por minuto, mas peticiones que eso 
se impodrian limitaciones al cliente por 15 minutos. La utilidad es interactiva
y su uso es auto explanatorio y guiado por prompts al usuario.

### Datos de FLUX.1 Schnell

Creado por los desarolladores y equipo de investigacion de "Black Forest Labs",
este modelo es una interacion de su modelo original "FLUX" con el enfoque 
en rapidez y balance de calidad de imagenes. Es un modelo del tipo `SOTA` o 
mejor conocidos como "Jack of All Trades" en espanol la mejor traduccion es
"El Caballo de Batalla".

`SAMPLE CODE:`
```python
  from together import Together
  client = Together()

  imageCompletion = client.images.generate(
    model="black-forest-labs/FLUX.1-schnell-Free",
    width=1024,
    height=1024,
    steps=4,
    prompt="Draw an anime style version of this image.",
    image_url="https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png",
  )

  print(imageCompletion.data[0].url)
```

#### Aqui hay que recalcar que esta linea `client = Together()` esta declarando que asume que el valor de la llave

si este no es el caso se tendria que declarar en la forma: `client = Togethe(api_key="YOUR_API_KEY")`

```python
  from together import Together
    
  client = Together(api_key="YOUR_API_KEY")

  imageCompletion = client.images.generate(
      model="black-forest-labs/FLUX.1-schnell-Free",
      width=1024,
      height=768,
      steps=4,
      prompt="Draw an anime style version of this image.",
      image_url="https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png",
  )

  print(imageCompletion.data[0].url)
```

---

# Media Detail Extractor

# Generador de Contenido SEO para YouTube

Esta es una herramienta de línea de comandos diseñada para automatizar la creación de metadatos optimizados para videos de YouTube. El script procesa archivos de video, extrae su contenido de texto mediante OCR y utiliza el modelo de IA Gemini 2.0 Flash de Google para generar títulos, descripciones y etiquetas (tags) listos para publicar.

Además, gestiona un catálogo en formato Excel con una cola de publicación automática.

## Funcionalidades Principales

* **Procesamiento en Lote**: Procesa un único archivo de video o un directorio completo de forma recursiva.
* **Extracción por OCR**: Utiliza Tesseract-OCR para leer subtítulos incrustados (hardsubs) directamente de los fotogramas del video.
* **Generación con IA**: Se conecta a la API de Gemini 2.0 Flash para crear contenido SEO:
  * **Títulos**: Optimizados para búsquedas, con un hashtag y de menos de 100 caracteres.
  * **Descripciones**: Atractivas y detalladas, con 3-5 hashtags para mejorar la visibilidad.
  * **Tags (Etiquetas)**: Una lista de 15 a 24 palabras clave relevantes, separadas por comas, listas para pegar en YouTube.
* **Catálogo en Excel**: Guarda automáticamente toda la información generada en un archivo `catalogo_videos.xlsx`.
* **Programación Automática**: Calcula y asigna una fecha y hora de publicación para cada video, siguiendo un patrón de 6 videos diarios (6 AM, 8 AM, 10 AM, 12 PM, 2 PM, 4 PM).

## Requisitos Previos

Antes de ejecutar el script, asegúrate de tener lo siguiente:

1. **Python 3.11+**.
2. **Tesseract-OCR**: El motor de OCR debe estar instalado en tu sistema y accesible a través del PATH del sistema.
    * Puedes descargarlo desde la [wiki de Tesseract en GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
3. **Clave de API de Google**: Necesitas una clave de API para el servicio de Gemini. Puedes obtenerla en [Google AI Studio](https://aistudio.google.com/app/apikey).

## Instalación y Configuración

1. **Clona o descarga el proyecto** en tu máquina local.

2. **Instala las dependencias**: Este proyecto usa `uv` para la gestión de paquetes. Abre una terminal en el directorio del proyecto y ejecuta:

```bash
uv pip sync pyproject.toml
```

3. **Crea el archivo de entorno**: En el directorio raíz del proyecto, crea un archivo llamado `.env`.

4. **Configura tu API Key**: Abre el archivo `.env` y añade tu clave de API de Google de la siguiente manera:

```ini
GOOGLE_API_KEY="TU_CLAVE_DE_API_AQUI"
```

## Modo de Uso

La herramienta se ejecuta desde la línea de comandos. Puedes pasarle la ruta a un solo archivo de video o a una carpeta que contenga múltiples videos.

* **Para procesar un solo archivo de video:**

```bash
uv run .\media-detailer.py "C:\ruta\completa\a\tu\video.mp4"
```

* **Para procesar un directorio completo de forma recursiva:**

```bash
uv run .\media-detailer.py "C:\ruta\completa\a\tu\carpeta_de_videos"
```

## Archivo de Salida: `catalogo_videos.xlsx`

El script creará o actualizará un archivo Excel con la siguiente estructura:

| ID Unico | Nombre del Archivo | Titulo | Descripcion | Hashtags (Tags) | Fecha de Catalogacion | Fecha de Programacion |
|---|---|---|---|---|---|---|
| ... | mi_video_01.mp4 | ... | ... | ... | ... | ... |
| ... | otro_video.mov | ... | ... | ... | ... | ... |

* **Hashtags (Tags)**: Esta columna contiene la lista de etiquetas separadas por comas, listas para ser pegadas en el campo "Etiquetas" de YouTube.
