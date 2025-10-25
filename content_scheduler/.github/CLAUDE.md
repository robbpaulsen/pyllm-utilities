# CLAUDE.md - Contexto del Proyecto para el Código de Claude

## Resumen del Proyecto

**Content Scheduler (Programador de Contenido)** es una herramienta de automatización basada en Python para la carga masiva y la programación de videos de YouTube utilizando la API de Datos de YouTube v3. El objetivo principal es reducir el tiempo dedicado a la publicación manual de videos de horas a minutos, separando las fases de carga y programación.

### Declaración del Problema

Publicar videos manualmente es lento y repetitivo:

- Tradicional: (Cargar → Metadatos → Programar) × N videos
- Puede llevar más de 8 horas para 30 videos.

### Enfoque de la Solución

Proceso automatizado de dos fases:

1. **Fase I - Carga Masiva**: Subir todos los videos como privados (rápido, con capacidad de paralelización)
2. **Fase II - Recolección de IDs**: Capturar los ID de video devueltos por la API
3. **Fase III - Programación Masiva**: Aplicar metadatos y fechas de publicación a todos los videos simultáneamente

**Ahorro de Tiempo**: Horas → Minutos

## Arquitectura y Componentes

### Scripts Principales

#### `uploader.py` - Carga Masiva de Videos

- **Propósito**: Subir múltiples archivos de video a YouTube como videos privados
- **Método de la API**: `youtube.videos().insert()`
- **Parámetros Clave**:
      - `media_body`: Ruta del archivo de video
      - `status.privacyStatus`: 'private' (privado)
      - Devuelve: `video_id` por cada carga
- **Salida**: Lista/archivo de ID de video para su posterior programación
- **Responsabilidades**:
      - Autenticación con OAuth 2.0
      - Iterar a través del directorio de videos
      - Subir videos con metadatos temporales/genéricos
      - Recoger y guardar los ID de video

#### `scheduler.py` - Aplicación Masiva de Metadatos y Programación

- **Propósito**: Aplicar metadatos completos y programar la publicación de los videos subidos
- **Método de la API**: `youtube.videos().update()`
- **Entrada**: CSV/Excel con las columnas:
      - ID de Video (desde el cargador)
      - Título (con hashtags)
      - Descripción (con hashtags al final)
      - Etiquetas \*(*Tags*) (cadena separada por comas → lista)
      - ID de Categoría (generalmente "27" para Educación)
      - Fecha/Hora de Publicación (formato ISO 8601)
- **Parámetros Clave**:
      ` json   {     "id": "ID_DE_VIDEO",     "snippet": {       "title": "Título con #hashtags",       "description": "Texto de la descripción #hashtag1 #hashtag2",       "tags": ["tag1", "tag2", "tag3"],       "categoryId": "27"     },     "status": {       "privacyStatus": "scheduled",       "publishAt": "2025-10-25T14:00:00Z",       "selfDeclaredMadeForKids": false     },     "contentDetails": {       "is3pContent": false     }   } `

### Flujo de Datos

```
[Directorio de Archivos de Video]
    ↓
[uploader.py] → API de YouTube (insertar) → [Videos Privados + IDs]
    ↓
[video_ids.csv/json] (guardado localmente)
    ↓
[Hoja de Cálculo de Metadatos] + [video_ids]
    ↓
[scheduler.py] → API de YouTube (actualizar) → [Videos Públicos Programados]
```

## Requisitos Técnicos

### Dependencias

- **Python**: \>=3.11
- **Administrador de Entornos**: `uv` (Astral)
- **Paquetes Requeridos**:
      - `google-api-python-client` - Cliente oficial de la API de Datos de YouTube
      - `google-auth-oauthlib` - Autenticación OAuth 2.0
      - `pandas` - Procesamiento de datos para metadatos CSV/Excel
      - `openpyxl` o `xlrd` - Soporte para archivos de Excel (si se utiliza .xlsx)

### Configuración de Autenticación

1. Proyecto en Google Cloud Console con la API de Datos de YouTube v3 habilitada
2. Credenciales OAuth 2.0 (*client\_secrets.json* o *client\_id.json*)
3. La primera ejecución requiere la autorización del usuario a través del navegador
4. Las ejecuciones posteriores utilizan el token almacenado (*token.pickle* o *token.json*)

### Estructura de Archivos Esperada

```
content_scheduler/
├── uploader.py
├── scheduler.py
├── pyproject.toml
├── README.md
├── CLAUDE.md (este archivo)
├── CHANGELOG.md
├── TODO.md
├── .venv/ (entorno virtual)
├── client_secrets.json (credenciales OAuth - NO HACER COMMIT)
├── token.pickle (token OAuth - NO HACER COMMIT)
├── videos/ (directorio con archivos de video)
├── metadata.csv o metadata.xlsx (datos de programación)
└── video_ids.csv (salida del uploader)
```

## Convenciones y Estándares de Código

### Estilo Python

- Seguir la guía de estilo PEP 8
- Usar sugerencias de tipos (*type hints*) para las firmas de funciones
- *Docstrings* para todas las funciones y clases
- Preferir f-strings para el formato de cadenas
- Usar *pathlib.Path* para las operaciones de archivos

### Manejo de Errores

- Implementar bloques *try-except* exhaustivos alrededor de las llamadas a la API
- Registrar todos los errores con contexto (nombre del archivo de video, ID de video, etc.)
- Continuar procesando los videos restantes si uno falla
- Proporcionar un informe de resumen al final (recuentos de éxitos/fallos)

### Registro (*Logging*)

- Usar el módulo `logging` de Python
- Niveles de registro:
      - INFO: Actualizaciones de progreso (video 1/30 subido)
      - WARNING: Problemas recuperables (falta un campo en los metadatos)
      - ERROR: Operaciones fallidas (falla en la carga)
      - DEBUG: Respuestas de la API, flujo detallado
- Registrar tanto en la consola como en un archivo (*content\_scheduler.log*)

### Configuración

- Usar variables de entorno o un archivo de configuración para:
      - Ruta del directorio de videos
      - Ruta del archivo de metadatos
      - Ruta del archivo de ID de video de salida
      - ID de categoría predeterminado
      - Estado de privacidad predeterminado
- No codificar rutas o credenciales de forma rígida

## Especificidades de la API de Datos de YouTube v3

### Consideraciones sobre la Cuota de la API

- Cuota diaria: 10,000 unidades (típico nivel gratuito)
- `videos.insert()`: 1600 unidades por llamada
- `videos.update()`: 50 unidades por llamada
- **Implicación**: \~6 cargas O \~200 actualizaciones por día (dentro de la cuota)
- Manejar con elegancia los errores de cuota excedida

### Limitación de Tasa (*Rate Limiting*)

- Implementar *exponential backoff* (retroceso exponencial) para errores de la API
- Respetar los límites de tasa de la API (evitar solicitudes rápidas y continuas)
- Considerar operaciones por lotes donde sea posible

### Flujo de Autenticación

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            credentials = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)
```

### Patrones Comunes de la API

#### Patrón de Carga (*Upload Pattern*)

```python
def upload_video(youtube, file_path):
    body = {
        'snippet': {
            'title': 'Título Temporal',
            'description': 'Descripción Temporal',
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'private',
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = request.execute()
    return response['id']
```

#### Patrón de Programación/Actualización (*Schedule/Update Pattern*)

```python
def schedule_video(youtube, video_id, metadata):
    body = {
        'id': video_id,
        'snippet': {
            'title': metadata['title'],
            'description': metadata['description'],
            'tags': metadata['tags'].split(','),
            'categoryId': metadata.get('category_id', '27')
        },
        'status': {
            'privacyStatus': 'scheduled',
            'publishAt': metadata['publish_at'],  # ISO 8601 UTC
            'selfDeclaredMadeForKids': False
        },
        'contentDetails': {
            'is3pContent': False
        }
    }

    request = youtube.videos().update(
        part='snippet,status,contentDetails',
        body=body
    )

    response = request.execute()
    return response
```

## Formato de Metadatos y Mejores Prácticas de SEO

### Etiquetas (*Tags*) (`snippet.tags`)

- Proporcionar como lista de cadenas: `["tag1", "tag2", "tag3"]`
- Formato de entrada en CSV: cadena separada por comas `"tag1,tag2,tag3"`
- Transformación: `tags_string.split(',')` → eliminar espacios en blanco
- Límite: \~500 caracteres en total (límite de YouTube)

### Hashtags (Título y Descripción)

- Incluir en el contenido de texto, no en la lista de etiquetas
- **Título**: Añadir hashtags relevantes al final: `"Gran Video #motivación #éxito"`
- **Descripción**: Añadir al final; YouTube muestra los 3 primeros por encima del título
- Formato: `#hashtag` (sin espacios en palabras múltiples: `#YouTubeShorts`)

### Formato de Fecha de Publicación

- **Requerido**: Formato ISO 8601 en zona horaria UTC
- Ejemplo: `"2025-10-25T14:00:00Z"`
- Debe ser al menos 15 minutos en el futuro
- Debe ser dentro de los 6 meses desde la fecha actual
- Conversión en Python: `datetime.isoformat() + 'Z'`

### ID de Categoría (Comunes)

- 27: Educación
- 22: Personas y Blogs (*People & Blogs*)
- 24: Entretenimiento
- 10: Música
- 23: Comedia
- Lista completa: [https://developers.google.com/youtube/v3/docs/videoCategories](https://developers.google.com/youtube/v3/docs/videoCategories)

## Caso de Uso: YouTube Shorts

Esta herramienta está optimizada para canales que publican grandes volúmenes de contenido de formato corto:

- Típico: 20-50 *shorts* por lote
- Duración: \<60 segundos cada uno
- Estructura de metadatos consistente
- Calendario de publicación regular (p. ej., diario a horas específicas)

### Consideraciones Específicas para *Shorts*

- Título: Mantener por debajo de los 60 caracteres para la visualización móvil
- Descripción: Las primeras 2-3 líneas son visibles, hacerlas impactantes
- Hashtags: Incluir \#Shorts para el algoritmo
- Miniatura (*Thumbnail*): La generada automáticamente suele ser adecuada
- Categoría: A menudo "24" (Entretenimiento) o "22" (Personas y Blogs)

## Flujo de Trabajo de Desarrollo

### Orden de Implementación

1. **Módulo de Autenticación** - Hacer que OAuth funcione primero
2. **uploader.py**:
       - Listar archivos de video desde el directorio
       - Subir con metadatos mínimos
       - Recolectar ID de video
       - Guardar ID en un archivo
3. **scheduler.py**:
       - Leer CSV/Excel de metadatos
       - Leer archivo de ID de video
       - Coincidir/fusionar datos
       - Actualizar videos con metadatos completos
       - Manejar fechas de programación
4. **Manejo de errores y registro (*logging*)** en todo el proceso
5. **Gestión de la configuración** (rutas, valores predeterminados)
6. **Pruebas** con lotes pequeños primero

### Estrategia de Pruebas

- **Canal de Desarrollo/Pruebas**: Usar un canal de YouTube separado para las pruebas
- **Lotes Pequeños**: Probar con 2-3 videos primero
- **Verificar Resultados**: Revisar YouTube Studio después de cada fase
- **Monitoreo de Cuota**: Rastrear el uso de la cuota de la API
- **Validación de Fecha**: Asegurar que las fechas programadas sean futuras y válidas

### Tareas Comunes

#### Adición de Nuevas Funcionalidades

- Nuevos campos de metadatos: Actualizar la lógica tanto de carga como de programación
- Nuevos formatos de archivo: Añadir lector en *scheduler.py* (*pandas* soporta muchos)
- Seguimiento del progreso del lote: Añadir base de datos/archivo de estado JSON
- Capacidad de reanudar: Rastrear cargas/programaciones completadas

#### Depuración (*Debugging*)

- Revisar `content_scheduler.log` para el flujo detallado
- Verificar la validez del token OAuth
- Comprobar la cuota de la API en Google Cloud Console
- Validar que la estructura del CSV de metadatos coincida con las columnas esperadas
- Probar las llamadas a la API con el Explorador de API de YouTube

## Seguridad y Protección

### Gestión de Secretos

- **NUNCA** hacer *commit* de `client_secrets.json` o `token.pickle`
- Añadir a `.gitignore`:
      `client_secrets.json   token.pickle   token.json   *.log   .venv/   __pycache__/`
- Almacenar las credenciales de forma segura (encriptadas si se comparten)

### Ámbitos (*Scopes*) de OAuth

- Solicitar los ámbitos mínimos necesarios
- Actual: `youtube.upload` (permisos completos de carga)
- Considerar: `youtube.force-ssl` para operaciones más amplias

### Seguridad de la API

- Implementar limitación de tasa para evitar bloqueos
- Validar todas las entradas del usuario antes de las llamadas a la API
- Usar cargas reanudables para archivos grandes
- Manejar las interrupciones de red con elegancia

## Restricciones y Limitaciones Importantes

1. **Cuota de la API**: Operaciones diarias limitadas (\~6 cargas completas/día en el nivel gratuito)
2. **Ventana de Programación**: 15 minutos de mínimo, 6 meses de máximo
3. **Tamaño del Archivo**: Máximo 256 GB por video (128 GB para la mayoría de las cuentas)
4. **Duración del Video**: Sin límite para cuentas verificadas; 15 min para no verificadas
5. **Límites de Metadatos**:
       - Título: 100 caracteres
       - Descripción: 5000 caracteres
       - Etiquetas (*Tags*): \~500 caracteres en total
6. **Límites de Tasa**: No documentados pero aplicados; usar *exponential backoff*

## Mejoras Futuras (del TODO.md)

Posibles funcionalidades a considerar:

- Automatización de la carga de miniaturas
- Creación y asignación de listas de reproducción
- Integración de analíticas (seguimiento del rendimiento)
- Interfaz web (Flask/FastAPI)
- Plantillas de programación (patrones recurrentes)
- Capacidad de deshacer/revertir
- Soporte multicanal
- Edición de video antes de la carga (integración de ffmpeg)

## Recursos y Referencias

- [Documentación de la API de Datos de YouTube v3](https://developers.google.com/youtube/v3/docs)
- [Videos: insert](https://developers.google.com/youtube/v3/docs/videos/insert)
- [Videos: update](https://developers.google.com/youtube/v3/docs/videos/update)
- [Cliente Python de la API de Google](https://github.com/googleapis/google-api-python-client)
- [OAuth 2.0 para Python](https://google-auth.readthedocs.io/)
- [Calculadora de Cuota de la API](https://developers.google.com/youtube/v3/determine_quota_cost)

## Notas para el Código de Claude

Al trabajar en este proyecto:

1. **Verificar las implicaciones de la cuota de la API** antes de implementar operaciones masivas
2. **Validar los formatos de fecha y hora** cuidadosamente (ISO 8601 UTC)
3. **Probar con conjuntos de datos pequeños** antes de escalar
4. **Preservar el contexto del error** en los registros (qué video falló y por qué)
5. **Manejar los fallos parciales** con elegancia (algunas cargas tienen éxito, otras fallan)
6. **Documentar los cambios de la API** (la API de YouTube evoluciona)
7. **Respetar los metadatos del usuario** - no modificar títulos/descripciones a menos que se solicite
8. **Verificar que los ámbitos de OAuth** coincidan con los permisos requeridos
9. **Considerar rutas de Windows** - usar *pathlib* para la compatibilidad multiplataforma

## Estado Actual del Proyecto

- **Fase**: Configuración/planificación inicial
- **Implementado**: *README.md*, estructura del proyecto definida
- **Pendiente**: Implementación completa de *uploader.py* y *scheduler.py*
- **Próximos Pasos**: Implementar la autenticación OAuth, luego la funcionalidad principal de *uploader.py*
