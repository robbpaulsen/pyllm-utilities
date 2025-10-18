# -*- coding: utf-8 -*-
"""
This script handles the bulk uploading of video files to YouTube as private videos.

It finds video files in a specified directory, authenticates with the YouTube API,
and uploads each file with temporary metadata. The resulting video IDs are saved
to a CSV file for later use by the scheduler script.
"""

import csv
import logging
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Import configuration and authentication modules from the local package
from content_scheduler import auth, config, logging_config

# A tuple of common video file extensions to look for.
VIDEO_FORMATS = (".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv")

def find_video_files():
    """Scans the configured video directory and returns a list of video files.

    Returns:
        list: A list of pathlib.Path objects for each found video file.
    """
    video_files = []
    if not config.VIDEOS_DIR.exists():
        logging.error(f"Videos directory not found: {config.VIDEOS_DIR}")
        return video_files

    logging.info(f"Searching for video files in: {config.VIDEOS_DIR}")
    for file_path in config.VIDEOS_DIR.iterdir():
        if file_path.suffix.lower() in VIDEO_FORMATS:
            video_files.append(file_path)
    return video_files

def save_video_ids(video_ids_with_filenames):
    """Saves the list of video IDs and their original filenames to a CSV file.

    Args:
        video_ids_with_filenames (list): A list of tuples, where each tuple contains
                                         (filename, video_id).
    """
    with open(config.VIDEO_IDS_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'video_id'])  # Write header
        writer.writerows(video_ids_with_filenames) # Write all data
    logging.info(f"Saved {len(video_ids_with_filenames)} video IDs to {config.VIDEO_IDS_FILE}")

def upload_videos():
    """Main function to orchestrate the video upload process."""
    # 1. Setup logging
    logging_config.setup_logging()
    logging.info("--- Starting YouTube Video Uploader ---")

    try:
        # 2. Authenticate and get the YouTube API service object
        youtube = auth.get_authenticated_service()
        
        # 3. Find all video files in the target directory
        video_files = find_video_files()

        if not video_files:
            logging.warning("No video files found to upload. Exiting.")
            return

        uploaded_videos = []
        total_videos = len(video_files)

        # 4. Loop through each video file and upload it
        for i, file_path in enumerate(video_files):
            logging.info(f"Uploading video {i + 1}/{total_videos}: {file_path.name}")

            # Prepare the basic metadata for the video
            body = {
                'snippet': {
                    'title': config.TEMPORARY_TITLE,
                    'description': config.TEMPORARY_DESCRIPTION,
                    'categoryId': config.DEFAULT_CATEGORY_ID
                },
                'status': {
                    'privacyStatus': config.DEFAULT_PRIVACY_STATUS,
                    'selfDeclaredMadeForKids': False
                }
            }

            try:
                # Prepare the media file for upload, making it resumable
                media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)
                
                # Create the API request
                request = youtube.videos().insert(
                    part='snippet,status',
                    body=body,
                    media_body=media
                )
                
                # Execute the request and get the response
                response = request.execute()
                video_id = response['id']
                uploaded_videos.append((file_path.name, video_id))
                logging.info(f"Successfully uploaded {file_path.name} with Video ID: {video_id}")

            except HttpError as e:
                logging.error(f"An HTTP error {e.resp.status} occurred while uploading {file_path.name}: {e.content}")
            except Exception as e:
                logging.error(f"An unexpected error occurred while uploading {file_path.name}: {e}")

        # 5. Save all collected video IDs and filenames to a CSV file
        if uploaded_videos:
            save_video_ids(uploaded_videos)

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred during the upload process: {e}")
    finally:
        logging.info("--- YouTube Video Uploader finished. ---")

# This allows the script to be run directly from the command line
if __name__ == "__main__":
    upload_videos()