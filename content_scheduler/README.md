# 🤖 Automatización de Carga y Programación Masiva en YouTube 🎥

## 🚀 Descripción del Proyecto

Este proyecto es un conjunto de **scripts de Python** diseñados para **automatizar y acelerar** el proceso de subir y programar videos en YouTube, utilizando la **YouTube Data API v3**.

La solución se enfoca en resolver un cuello de botella común: el tiempo que se invierte en configurar manualmente la metadata (título, descripción, etiquetas, fecha) video por video. Al separar la carga masiva (rápida) de la programación masiva (rápida), se busca reducir un proceso que podría tomar horas (ej. 8 horas para 30 videos) a solo minutos.

```bash
content_scheduler/
├── uploader.py      # Script principal ejecutable
├── pyproject.toml   # Dependencias mínimas
├── scheduler.py     # Prgrama hora y dia de publicacion
├── CHANGELOG.md     # Tracker de cambios
├── TODO.md          # tareas pendientes por hacer
└── README.md        # Instrucciones básicas
```

### Canal de Aplicación

Dada la necesidad de gestionar un alto volumen de contenido de corta duración, este enfoque es ideal para el canal:

- **@TUCANAL** o la carga masiva de **YouTube Shorts**.

## 💡 El Enfoque de la Solución: Separación de Tareas

El método tradicional de publicación es lento y repetitivo:

> _MANUAL:_ (Subir, Metadata, Programar) 🔁 (Subir, Metadata, Programar)...

El enfoque automatizado optimiza esto en dos fases distintas, aprovechando la velocidad de la API:

1. **Carga Masiva (Script 1):** Subir todos los archivos de video en el menor tiempo posible, dejándolos en estado **Privado**.

2. **Programación Masiva (Script 2)::** Aplicar la metadata completa (Título, Descripción, Tags, Fecha de Publicación) de forma **simultánea** a todos los videos subidos, ahorrando la configuración manual.

---

## Estado Actual y Flujo de Trabajo

Actualmente, el proyecto se encuentra en un estado **parcialmente automatizado** debido a los requisitos de verificación de YouTube.

### `uploader.py` (100% Funcional)

El script de carga masiva es completamente funcional. Permite subir múltiples videos a tu canal de YouTube y dejarlos en estado **`privado`**. Este script maneja la autenticación para Cuentas de Marca, permitiéndote seleccionar el canal correcto al iniciar sesión.

### `scheduler.py` (Dependiente de Verificación)

El script de programación masiva está implementado, pero su ejecución exitosa depende de que tu canal de YouTube tenga las **"Funciones Avanzadas"** habilitadas. YouTube requiere una verificación (por lo general con un documento de identidad o video-verificación) para permitir la programación de videos a través de la API.

### Flujo de Trabajo Recomendado

Mientras tu canal completa el proceso de verificación, el flujo de trabajo recomendado es el siguiente:

1.  **Carga Masiva (Automática):** Ejecuta `uploader.py` para subir todos tus videos de una sola vez. Esto te ahorrará la mayor parte del tiempo manual.
2.  **Programación (Manual):** Una vez que los videos estén en tu canal como privados, accede a **YouTube Studio** y, desde la sección de "Contenido", edita cada video para añadirle su título, descripción y fecha de programación final.

Este método híbrido sigue representando un ahorro de tiempo significativo comparado con el proceso completamente manual.

## 🛠️ Requisitos e Instalación

### Requisitos Previos

Para poder ejecutar este proyecto, necesitarás:

1. **Google Console (Cloud Project):** Habilitar la **YouTube Data API v3** para tu proyecto y obtener las credenciales de OAuth 2.0.

2. **Archivos de Video:** Una carpeta con los videos listos para subir.

3. **Archivo de Datos:** Un archivo (CSV o Excel) que contenga la lista de títulos, descripciones, etiquetas y las fechas de publicación deseadas para cada video.

### Dependencias de Python

Gestionaremos el entorno con **`uv`**, tu gestor de librerías preferido:

|**Herramienta**|**Uso**|
|---|---|
|**`uv`** (Astral)|Gestor de entornos virtuales y dependencias.|
|**`google-api-python-client`**|Biblioteca oficial de Google para interactuar con la YouTube Data API.|
|**`pandas`**|Para leer y gestionar eficientemente los datos del archivo CSV/Excel de programación.|

Bash

```
# 1. Crear el entorno virtual con uv
uv venv

# 2. Activar el entorno virtual
source .venv/bin/activate  # (En Linux/macOS)
.venv\Scripts\activate     # (En Windows)

# 3. Instalar las dependencias
uv pip install google-api-python-client pandas
```

---

## 📜 Flujo de Trabajo en Tres Fases

El proyecto está dividido conceptualmente en tres fases, manejadas por los dos scripts principales.

|**Fase**|**Script**|**Acción Clave de la API**|**Resultado**|
|---|---|---|---|
|**I: Carga Masiva**|`uploader.py`|`youtube.videos().insert(..., media_body=video_file, **status='private'**)`|Sube todos los videos a YouTube en modo **Privado** con un título temporal.|
|**II: Recolección de IDs**|`uploader.py`|La llamada `insert` **retorna el `video_id`**.|Genera una lista de todos los `Video IDs` recién creados (Ej. `['v12345', 'v67890', ...]` ).|
|**III: Programación Masiva**|`scheduler.py`|`youtube.videos().update(..., body={'id': video_id, 'status': {...}})`|Itera sobre la lista de IDs y aplica el Título, Descripción, Tags y la fecha de publicación (`'privacyStatus': 'scheduled'`).|

---

## ⚙️ Integración de Metadata (SEO)

La programación masiva se vuelve tan eficiente porque en un solo llamado de API (`update`) se incluye toda la metadata necesaria para el SEO del video.

### 1. Etiquetas de Video (`tags`)

Las etiquetas son palabras clave que ayudan a la clasificación del contenido. Se envían como una **lista de cadenas de texto** dentro de la propiedad `snippet`.

|**Propiedad de la API**|**Ejemplo de Datos de Entrada (CSV)**|**Transformación en Python**|
|---|---|---|
|`snippet.tags`|`"motivacion,shorts,productividad"`|`tags_string.split(',')` $\rightarrow$ `["motivacion", "shorts", ...]`|

### 2. Hashtags en Título y Descripción

Los hashtags se integran directamente en las propiedades de texto `snippet.title` y `snippet.description`.

- **Título (`snippet.title`):** Incluye los hashtags relevantes al final del título (Ej: `Título Increíble #motivacion #exito`).

- **Descripción (`snippet.description`):** Es una buena práctica colocarlos al final de la descripción. YouTube puede mostrar hasta tres de estos hashtags sobre el título del video publicado.

### 3. Estructura Final del `Body` (Fase III)

El script de programación (`script_2_schedule.py`) construye y envía un objeto JSON similar a este para cada video:

```json
{
  "id": "TU_VIDEO_ID_GENERADO",
  "snippet": {
    "title": "EL TÍTULO FINAL: Con Hashtags #motivacion",
    "description": "La descripción larga y optimizada. #exito",
    "tags": ["motivacion", "shorts", "productividad", "uv"],
    "categoryId": "27"
  },
  "status": {
    "privacyStatus": "scheduled",
    "publishAt": "2025-10-25T14:00:00Z", // Formato ISO 8601 UTC
    "selfDeclaredMadeForKids": false
  },
  "contentDetails": {
    "is3pContent": false 
  }
}
```

# Subir tus videos a tu canal de YouTube:

## **Con tu entorno virtual activado, habiendo instalado las dependencias y ya con tus credenciales
`client_secrets.json` en la raiz del directorio de la utilidad, navega al directorio `src/` del proyecto. 
Aqui ejecutaras:

```python
uv run -m content_scheduler.uploader
```

Se abrira tu navegador y te dirigira a que escojas la identidad o correo al que esta unido tu canal
de YouTube, detenidamente si tienes mas de un correo escoge el correcto ya que el equivocarte involucra
muchos dolores de cabeza. 

Ya que escogiste la cuenta correcta aceptas que estas conciente que una aplicacion
quiere conectarse a tu cuenta, aceptas todo y ya se valida el acceso, y la utilidad inicia el procesamiento 
de todos los videos que esten en el directori `videos/`.

Al terminar esribira un archivo CSV con los identificdores de tus videos, nombre, y estado de publicacion. 

Por el momento todos se cargan con el estado de privados, ya que es necesario si quieres poder despues programar
la publicacion de cada uno en una fecha y hora especifica.**