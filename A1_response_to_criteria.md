Assignment 1 - REST API Project - Response to Criteria
================================================

Overview
------------------------------------------------

- **Name:** Hsin-Yu Chou
- **Student number:** n11696630
- **Application name:** web filter app
- **Two line description:** This full-stack application allows users to upload images and videos, apply custom LUT filters, and download the results. It features user authentication, a personal media library, and Pexels API integration for sourcing images and videos.


Core criteria
------------------------------------------------

### Containerise the app

- **ECR Repository name:** filter-app-backend, filter-app-frontend, filter-app-nginx
- **Video timestamp:**
- **Relevant files:**
    - backend/Dockerfile
    - frontend/Dockerfile
    - nginx/Dockerfile
    - docker-compose.yml
    - docker-compose.prod.yml
    - .dockerignore
    - build-and-push.sh 

### Deploy the container

- **EC2 instance ID:** i-02ea8d7c6306bc80e
- **Video timestamp:**

### User login

- **One line description:** Hard-coded username/password list.  Using JWTs for sessions.
- **Video timestamp:**
- **Relevant files:**
    - backend/routers/auth.py
    - frontend/src/components/LoginView.jsx 

### REST API

- **One line description:** A RESTful API built with FastAPI to manage media, filters, user authentication, and processing tasks.
- **Video timestamp:**
- **Relevant files:**
    - backend/main.py (API entrypoint)
    - backend/routers/ (Contains all API endpoints like auth.py, filters.py, media.py, etc.)
    - backend/models/schemas.py (Defines API data structures) 

### Data types

- **One line description:** Manages both structured (metadata for media/filters) and unstructured (the files themselves) data.
- **Video timestamp:**
- **Relevant files:**
    - backend/models/schemas.py
    - backend/utils/database.py
    - storage/

#### First kind

- **One line description:** Structured JSON data representing the metadata for media and filters.
- **Type:** Structured
- **Rationale:** This data has a predefined schema (Pydantic models) and is stored in a key-value format (like a JSON file), allowing for queries and management.
- **Video timestamp:**
- **Relevant files:**
    - backend/models/schemas.py
    - backend/utils/database.py

#### Second kind

- **One line description:** Raw binary files for media (images/videos) and LUT filters.
- **Type:** Unstructured
- **Rationale:** These are files stored directly on the filesystem. The application treats them as opaque blobs for storage and processing, without enforcing a schema on their internal content.
- **Video timestamp:**
- **Relevant files:**
    - storage/media_uploads/
    * storage/filter_uploads/
    - backend/services/process_media.py 

### CPU intensive task

- **One line description:** Applying .cube LUT filters to user-uploaded images and videos using the ffmpeg library.
- **Video timestamp:**
- **Relevant files:**
    - backend/services/process_media.py (Contains the core FFmpeg processing logic)
    - backend/routers/process.py (The API endpoint that triggers the task)
    - backend/assets/luts/ (Directory containing the LUT filter files)

### CPU load testing

- **One line description:** CPU load was tested by manually uploading a long video file to the processing endpoint to observe performance under sustained load.
- **Video timestamp:**
- **Relevant files:**
    - backend/services/process_media.py (The service under test)
    - backend/routers/process.py (The endpoint used for the test)

Additional criteria
------------------------------------------------

### Extensive REST API features

- **One line description:** The API includes advanced features such as URL-based versioning (/api/v1) and limit-offset pagination on list endpoints.
- **Video timestamp:**
- **Relevant files:**
    - backend/main.py (Implements the /v1 prefix)
    - backend/routers/media.py (Implements pagination)
    - backend/routers/filters.py (Implements pagination)

### External API(s)

- **One line description:** Integrates with the Pexels API to allow users to search for and import stock images.
- **Video timestamp:**
- **Relevant files:**
    - backend/routers/pexels.py

### Additional types of data

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**


### Custom processing

- **One line description:** The application provides custom media processing by applying user-selected .cube LUT filters to uploaded images and videos via FFmpeg.
- **Video timestamp:**
- **Relevant files:**
    - backend/services/process_media.py
    - backend/routers/process.py

### Infrastructure as code

- **One line description:** Used a declarative Docker Compose file (docker-compose.prod.yml) and a shell script (build-and-push.sh) to automate the setup and deployment of the application services.
- **Video timestamp:**
- **Relevant files:**
    - docker-compose.prod.yml
    - build-and-push.sh

### Web client

- **One line description:** A modern web client built with React, allowing users to log in, upload/manage media, and apply filters.
- **Video timestamp:**
- **Relevant files:**
    - frontend/ (The entire directory)
    - frontend/src/App.jsx
    - frontend/src/components/

### Upon request

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**
    