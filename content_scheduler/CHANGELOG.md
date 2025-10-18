# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2025-10-18

### **Phase 0: Project Foundation and Setup**

### Completed
- **Project Structure**: Created `src/content_scheduler` and `tests` directories.
- **Dependency Management**: Added production and development dependencies using `uv`.
- **Authentication Module**: Implemented a reusable OAuth 2.0 flow in `src/content_scheduler/auth.py`.
- **Configuration Module**: Created `src/content_scheduler/config.py` for managing paths and settings.
- **Logging Module**: Set up a centralized logger in `src/content_scheduler/logging_config.py`.
- **Initial Tests**: Configured `pytest` and created a basic test to ensure the project structure is sound.
- **Code Quality**: Configured `ruff` in `pyproject.toml`.

### **Phase 1: Uploader Implementation**

### Completed
- **Uploader Logic**: Implemented the main logic for listing and iterating through video files.
- **API Interaction**: Successfully uploaded videos using the `videos().insert()` call.
- **ID Collection**: Captured and stored the returned `video_id` for each uploaded video.
- **Error Handling & Authentication**: Successfully navigated complex authentication issues related to Brand Accounts and OAuth credential types.

### **Phase 2: Scheduler Implementation**

### Planned
- **Scheduler Logic**: Implement logic to read `video_ids.csv` and `metadata.csv` using pandas.
- **Data Merging**: Combine the two data sources based on the `filename` column.
- **API Interaction**: Implement the `videos().update()` call to apply the final metadata and schedule the videos.
- **Feedback and Error Handling**: Integrate logging for the scheduling process.
- **Unit Tests**: Write a unit test for the scheduler.
