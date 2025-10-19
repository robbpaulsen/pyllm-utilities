import os
import uuid
import pandas as pd
import google.generativeai as genai
import json
import click
import mimetypes
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env para la configuración de la API Key.
load_dotenv()

# --- Configuración de la API de Gemini ---
try:
    # Intenta configurar la API de Gemini usando la clave del entorno.
    # Falla de manera controlada si la clave no se encuentra.
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY no encontrada. Por favor, crea un archivo .env y añade tu clave.")
    exit()

# --- Constantes del Proyecto ---
EXCEL_FILE = "catalogo_videos.xlsx"  # Nombre del archivo Excel de salida.
SCHEDULE_HOURS = [6, 8, 10, 12, 14, 16]  # Horas predefinidas para la programación de videos.
VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv", ".avi", ".wmv"]  # Extensiones de video soportadas.
COLUMNS = [
    "ID Unico",
    "Nombre del Archivo",
    "Titulo",
    "Descripcion",
    "Hashtags",
    "Fecha de Catalogacion",
    "Fecha de Programacion",
]

# --- Funciones Principales ---

def get_next_schedule_datetime(start_date_str="2025-10-20"):
    '''
    Calcula la próxima fecha y hora de programación disponible.
    Si el archivo Excel no existe, comienza desde la fecha de inicio.
    Si existe, lee la última fecha programada y calcula el siguiente horario
    disponible en el mismo día o al día siguiente.
    '''
    if not os.path.exists(EXCEL_FILE):
        # Si no hay catálogo, programa el primer video en el primer horario del día de inicio.
        return datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            # Si el catálogo está vacío, usa la fecha de inicio.
            return datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)
        
        # Obtiene la última fecha de programación y calcula la siguiente.
        last_schedule_str = df["Fecha de Programacion"].iloc[-1]
        last_schedule = pd.to_datetime(last_schedule_str)
        last_hour = last_schedule.hour

        if last_hour < SCHEDULE_HOURS[-1]:
            # Si aún hay horarios disponibles en el mismo día, toma el siguiente.
            next_hour_index = SCHEDULE_HOURS.index(last_hour) + 1
            return last_schedule.replace(hour=SCHEDULE_HOURS[next_hour_index], minute=0, second=0)
        else:
            # Si no, pasa al primer horario del día siguiente.
            next_day = last_schedule + timedelta(days=1)
            return next_day.replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)
    except Exception as e:
        # En caso de error, regresa a la fecha de inicio como fallback.
        print(f"Error leyendo o procesando el archivo Excel: {e}")
        return datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)

def analyze_video_with_gemini(video_path: str) -> str:
    '''
    Analiza un archivo de video usando el modelo multimodal Gemini.
    Envía el video "en línea" para evitar errores de la API relacionados con RAG.
    Retorna un resumen textual del contenido del video.
    '''
    print(f"Analizando video {os.path.basename(video_path)} con Gemini 2.0 Flash...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    try:
        # Determina el tipo MIME del video para enviarlo correctamente a la API.
        mime_type, _ = mimetypes.guess_type(video_path)
        if mime_type is None:
            mime_type = "video/mp4"  # Usa un valor por defecto si no se puede determinar.

        print(f"Cargando y enviando {os.path.basename(video_path)} ({mime_type}) en línea...")
        
        # Lee los bytes del video para enviarlos directamente en la solicitud.
        with open(video_path, "rb") as f:
            video_data = f.read()

        # Construye la solicitud multimodal con los datos del video y el prompt.
        prompt_parts = [
            {
                "mime_type": mime_type,
                "data": video_data
            },
            "Analiza este video y proporciona un resumen completo de su contenido, temas clave y cualquier texto u objeto prominente. Enfócate en información útil para generar metadatos SEO para YouTube (título, descripción, hashtags, etiquetas). Proporciona la salida como un párrafo detallado."
        ]

        response = model.generate_content(prompt_parts)

        if response.text:
            print(f"Análisis con Gemini completo para {os.path.basename(video_path)}.")
            return response.text
        else:
            print(f"Gemini no retornó texto para {os.path.basename(video_path)}.")
            return ""
    except Exception as e:
        print(f"Error analizando el video {os.path.basename(video_path)} con Gemini: {e}")
        return ""

def generate_youtube_content(video_text: str) -> dict | None:
    '''
    Usa el resumen del video para generar metadatos SEO para YouTube en formato JSON.
    '''
    print("Generando contenido de YouTube con Gemini 2.0 Flash...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    # Se asegura de que el texto del video sea un string JSON válido para el prompt.
    safe_video_text = json.dumps(video_text)
    
    # Prompt diseñado para obtener una salida JSON estructurada y consistente.
    prompt = f'''
    Basado en el siguiente texto de un video, genera metadatos para un video de YouTube.
    La salida debe ser un objeto JSON válido con tres claves: "title", "description", y "tags".

    **Requisitos:**
    1.  **title**: Un título atractivo y optimizado para SEO. DEBE incluir un hashtag relevante. La cadena completa (título + hashtag) NO DEBE exceder los 100 caracteres.
    2.  **description**: Una descripción detallada y atractiva que enganche al lector. DEBE incluir de 3 a 5 hashtags relevantes para la visibilidad.
    3.  **tags**: Una sola cadena de texto con 15 a 24 etiquetas relevantes, separadas por comas, para la sección de etiquetas de YouTube.

    **Texto del Video:**
    {safe_video_text}
    '''
    try:
        response = model.generate_content(prompt)
        # Limpia la respuesta para asegurar que sea un JSON válido, eliminando los bloques de código de Markdown.
        cleaned_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        content = json.loads(cleaned_json, strict=False)
        
        # Valida que el JSON generado contenga todas las claves esperadas.
        if not all(k in content for k in ['title', 'description', 'tags']):
            print("Error: El contenido generado no tiene las claves requeridas.")
            return None
        return content
    except Exception as e:
        print(f"Error llamando a la API de Gemini o parseando la respuesta: {e}")
        return None

def update_excel_sheet(data: dict):
    '''
    Actualiza o crea el archivo Excel con una nueva fila de datos del video.
    '''
    new_row = pd.DataFrame([data], columns=COLUMNS)
    if not os.path.exists(EXCEL_FILE):
        # Si el archivo no existe, lo crea con las columnas definidas.
        df = pd.DataFrame(columns=COLUMNS)
    else:
        # Si ya existe, lo lee para añadir la nueva fila.
        df = pd.read_excel(EXCEL_FILE)
    
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"Se actualizó correctamente {EXCEL_FILE} con {data['Nombre del Archivo']}")

def _process_single_video(video_path: str):
    '''
    Orquesta el flujo de procesamiento para un único archivo de video.
    '''
    click.echo(f"--- Iniciando procesamiento para: {os.path.basename(video_path)} ---")
    
    # 1. Obtener el próximo horario disponible.
    schedule_datetime = get_next_schedule_datetime()
    click.echo(f"Próximo horario disponible: {schedule_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. Analizar el video con Gemini para obtener un resumen.
    video_text = analyze_video_with_gemini(video_path)
    if not video_text:
        click.echo(f"Error: No se pudo extraer texto de {os.path.basename(video_path)}. Saltando.")
        return
        
    # 3. Generar contenido de YouTube a partir del resumen.
    youtube_content = generate_youtube_content(video_text)
    if not youtube_content:
        click.echo(f"Error: No se pudo generar contenido de YouTube para {os.path.basename(video_path)}. Saltando.")
        return
        
    # 4. Preparar los datos para guardar en Excel.
    data = {
        "ID Unico": str(uuid.uuid4()),
        "Nombre del Archivo": os.path.basename(video_path),
        "Titulo": youtube_content["title"],
        "Descripcion": youtube_content["description"],
        "Hashtags": youtube_content["tags"],
        "Fecha de Catalogacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Fecha de Programacion": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # 5. Actualizar la hoja de cálculo.
    try:
        update_excel_sheet(data)
        click.echo(f"Proceso completo para {os.path.basename(video_path)}.")
    except Exception as e:
        click.echo(f"Error actualizando la hoja de Excel para {os.path.basename(video_path)}: {e}")

@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True))
@click.option('--output-dir', default='./output', help='Directorio para guardar archivos de salida.')
@click.option('--log-level', default='INFO', help='Establecer el nivel de logging.')
def process_path(path, output_dir, log_level):
    '''
    Punto de entrada del script. Procesa un solo archivo de video o un directorio
    de videos de forma recursiva.
    '''
    click.echo(f"Log Level: {log_level}, Output Dir: {output_dir}")
    
    files_to_process = []
    if os.path.isfile(path):
        # Si la ruta es un archivo, lo añade a la lista.
        files_to_process.append(path)
    elif os.path.isdir(path):
        # Si es un directorio, busca recursivamente archivos de video.
        click.echo(f"Escaneando directorio: {path}")
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                    files_to_process.append(os.path.join(root, filename))
    
    if not files_to_process:
        click.echo("No se encontraron archivos de video para procesar.")
        return

    total_files = len(files_to_process)
    click.echo(f"Se encontraron {total_files} archivo(s) de video para procesar.")

    # Itera sobre cada archivo y lo procesa.
    for i, file_path in enumerate(files_to_process):
        click.echo(f"\n[Procesando archivo {i+1} de {total_files}]")
        _process_single_video(file_path)

if __name__ == '__main__':
    # Ejecuta el comando principal de Click.
    process_path()
