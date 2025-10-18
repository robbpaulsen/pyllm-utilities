import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from . import config


def get_authenticated_service():
    """
    Authenticates with the YouTube API and returns a service object.
    Handles token refreshing and new user authorization.
    """
    credentials = None

    # Load existing credentials if available
    if os.path.exists(config.TOKEN_PICKLE_FILE):
        with open(config.TOKEN_PICKLE_FILE, 'rb') as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(config.CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Error: The OAuth client secrets file '{config.CLIENT_SECRETS_FILE.name}' was not found. "
                    f"Please download it from your Google Cloud project and place it in the root directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CLIENT_SECRETS_FILE, config.SCOPES)
            credentials = flow.run_local_server(port=0, prompt='select_account')

        # Save the credentials for the next run
        with open(config.TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)

if __name__ == '__main__':
    # This allows for testing the authentication flow directly
    try:
        print("Attempting to authenticate with YouTube...")
        youtube_service = get_authenticated_service()
        print("Authentication successful!")
        print("Service object created:", youtube_service)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred during authentication: {e}")
