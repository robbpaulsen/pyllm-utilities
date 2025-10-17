import os
import uuid
import pandas as pd
import google.generativeai as genai
import pytesseract
import cv2
import json
import click
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY not found. Please create a .env file and add your key.")
    exit()

# --- Constants ---
EXCEL_FILE = "catalogo_videos.xlsx"
SCHEDULE_HOURS = [6, 8, 10, 12, 14, 16]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv", ".avi", ".wmv"]
COLUMNS = [
    "ID Unico",
    "Nombre del Archivo",
    "Titulo",
    "Descripcion",
    "Hashtags",
    "Fecha de Catalogacion",
    "Fecha de Programacion",
]

# --- Core Functions ---

def get_next_schedule_datetime(start_date_str="2025-10-20"):
    if not os.path.exists(EXCEL_FILE):
        return datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            return datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)
        last_schedule_str = df["Fecha de Programacion"].iloc[-1]
        last_schedule = pd.to_datetime(last_schedule_str)
        last_hour = last_schedule.hour
        if last_hour < SCHEDULE_HOURS[-1]:
            next_hour_index = SCHEDULE_HOURS.index(last_hour) + 1
            return last_schedule.replace(hour=SCHEDULE_HOURS[next_hour_index], minute=0, second=0)
        else:
            next_day = last_schedule + timedelta(days=1)
            return next_day.replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)
    except Exception as e:
        print(f"Error reading or processing Excel file: {e}")
        return datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=SCHEDULE_HOURS[0], minute=0, second=0)

def extract_text_from_video(video_path: str) -> str:
    print(f"Extracting text from video (OCR)... This may take a while.")
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file: {video_path}")
            return ""
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0: fps = 30
        all_text = []
        last_text = ""
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            if frame_count % int(fps) == 0:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                try:
                    text = pytesseract.image_to_string(gray_frame, lang='eng+spa').strip()
                    if text and text != last_text:
                        all_text.append(text)
                        last_text = text
                except pytesseract.TesseractNotFoundError:
                    print("Error: Tesseract is not installed or not in your PATH.")
                    return ""
                except Exception as ocr_error:
                    print(f"An error occurred during OCR on {video_path}: {ocr_error}")
            frame_count += 1
        cap.release()
        full_text = "\n".join(all_text)
        print(f"OCR complete for {os.path.basename(video_path)}. Extracted {len(full_text)} characters.")
        return full_text
    except Exception as e:
        print(f"An error occurred while processing {video_path}: {e}")
        return ""

def generate_youtube_content(video_text: str) -> dict | None:
    print("Generating YouTube content with Gemini 2.0 Flash...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    safe_video_text = json.dumps(video_text)
    prompt = f'''
    Based on the following text from a video, generate metadata for a YouTube video.
    The output must be a valid JSON object with three keys: "title", "description", and "tags".

    **Requirements:**
    1.  **title**: A catchy, SEO-optimized title. It MUST include one relevant hashtag. The entire string (title + hashtag) MUST NOT exceed 100 characters.
    2.  **description**: A detailed and engaging description that hooks the reader. It MUST include 3 to 5 relevant hashtags for discoverability.
    3.  **tags**: A single string containing 15 to 24 relevant, comma-separated tags for YouTube's tag section.

    **Video Text:**
    {safe_video_text}
    '''
    try:
        response = model.generate_content(prompt)
        cleaned_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        content = json.loads(cleaned_json, strict=False)
        if not all(k in content for k in ['title', 'description', 'tags']):
            print("Error: Generated content is missing required keys.")
            return None
        return content
    except Exception as e:
        print(f"Error calling Gemini API or parsing response: {e}")
        return None

def update_excel_sheet(data: dict):
    new_row = pd.DataFrame([data], columns=COLUMNS)
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=COLUMNS)
    else:
        df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"Successfully updated {EXCEL_FILE} with {data['Nombre del Archivo']}")

def _process_single_video(video_path: str):
    """Core logic to process a single video file."""
    click.echo(f"--- Starting processing for: {os.path.basename(video_path)} ---")
    schedule_datetime = get_next_schedule_datetime()
    click.echo(f"Next schedule slot: {schedule_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    video_text = extract_text_from_video(video_path)
    if not video_text:
        click.echo(f"Error: Could not extract text from {os.path.basename(video_path)}. Skipping.")
        return
    youtube_content = generate_youtube_content(video_text)
    if not youtube_content:
        click.echo(f"Error: Could not generate YouTube content for {os.path.basename(video_path)}. Skipping.")
        return
    data = {
        "ID Unico": str(uuid.uuid4()),
        "Nombre del Archivo": os.path.basename(video_path),
        "Titulo": youtube_content["title"],
        "Descripcion": youtube_content["description"],
        "Hashtags": youtube_content["tags"],
        "Fecha de Catalogacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Fecha de Programacion": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        update_excel_sheet(data)
        click.echo(f"Process complete for {os.path.basename(video_path)}.")
    except Exception as e:
        click.echo(f"Error updating Excel sheet for {os.path.basename(video_path)}: {e}")

@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True))
@click.option('--output-dir', default='./output', help='Directory to save output files.')
@click.option('--log-level', default='INFO', help='Set the logging level.')
def process_path(path, output_dir, log_level):
    """Processes a single video file or a directory of video files recursively."""
    click.echo(f"Log Level: {log_level}, Output Dir: {output_dir}")
    
    files_to_process = []
    if os.path.isfile(path):
        files_to_process.append(path)
    elif os.path.isdir(path):
        click.echo(f"Scanning directory: {path}")
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                    files_to_process.append(os.path.join(root, filename))
    
    if not files_to_process:
        click.echo("No video files found to process.")
        return

    total_files = len(files_to_process)
    click.echo(f"Found {total_files} video file(s) to process.")

    for i, file_path in enumerate(files_to_process):
        click.echo(f"\n[Processing file {i+1} of {total_files}]")
        _process_single_video(file_path)

if __name__ == '__main__':
    process_path()