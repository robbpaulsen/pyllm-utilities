import logging
import pandas as pd
from googleapiclient.errors import HttpError

from content_scheduler import auth, config, logging_config

def schedule_videos():
    """Reads video metadata and schedules the videos for publication."""
    logging_config.setup_logging()
    logging.info("--- Starting YouTube Video Scheduler ---")

    try:
        # --- 1. Authentication and Data Loading ---
        youtube = auth.get_authenticated_service()

        if not config.VIDEO_IDS_FILE.exists() or not config.METADATA_FILE.exists():
            logging.error("Error: Missing required files. Please ensure both 'video_ids.csv' and 'metadata.csv' exist.")
            return

        ids_df = pd.read_csv(config.VIDEO_IDS_FILE)
        metadata_df = pd.read_csv(config.METADATA_FILE)

        # --- 2. Data Merging ---
        if 'filename' not in metadata_df.columns:
            logging.error("'metadata.csv' is missing the required 'filename' column.")
            return
        
        schedule_df = pd.merge(ids_df, metadata_df, on='filename')

        if schedule_df.empty:
            logging.warning("No matching videos found between video_ids.csv and metadata.csv. Nothing to schedule.")
            return

        # --- 3. API Update Loop ---
        total_videos = len(schedule_df)
        for index, row in schedule_df.iterrows():
            video_id = row['video_id']
            logging.info(f"Scheduling video {index + 1}/{total_videos}: {video_id} ({row['filename']})")

            try:
                # --- 4. Construct API Request Body ---
                body = {
                    'id': video_id,
                    'snippet': {
                        'title': row['title'],
                        'description': row['description'],
                        'tags': [tag.strip() for tag in str(row['tags']).split(',')],
                        'categoryId': str(row.get('categoryId', config.DEFAULT_CATEGORY_ID))
                    },
                    'status': {
                        'privacyStatus': 'scheduled',
                        'publishAt': row['publish_at'],
                        'selfDeclaredMadeForKids': False
                    }
                }

                # --- 5. Execute API Call ---
                youtube.videos().update(
                    part='snippet,status',
                    body=body
                ).execute()

                logging.info(f"Successfully scheduled video {video_id} for {row['publish_at']}")

            except HttpError as e:
                logging.error(f"An HTTP error {e.resp.status} occurred while scheduling {video_id}: {e.content}")
            except Exception as e:
                logging.error(f"An unexpected error occurred while scheduling {video_id}: {e}")

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        logging.info("--- YouTube Video Scheduler finished. ---")

if __name__ == "__main__":
    schedule_videos()
