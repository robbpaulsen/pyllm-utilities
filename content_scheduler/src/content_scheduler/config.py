from pathlib import Path

# --- Project Root ---
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# --- OAuth Settings ---
CLIENT_SECRETS_FILE = ROOT_DIR / 'client_secrets.json'
TOKEN_PICKLE_FILE = ROOT_DIR / 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube']

# --- File/Directory Paths ---
VIDEOS_DIR = ROOT_DIR / 'videos'
METADATA_FILE = ROOT_DIR / 'metadata.csv'
VIDEO_IDS_FILE = ROOT_DIR / 'video_ids.csv'
LOG_FILE = ROOT_DIR / 'content_scheduler.log'

# --- YouTube API Defaults ---
DEFAULT_CATEGORY_ID = '27'  # Education
DEFAULT_PRIVACY_STATUS = 'private'

# --- Uploader Settings ---
TEMPORARY_TITLE = 'Temporal Title'
TEMPORARY_DESCRIPTION = 'Temporal Description'
