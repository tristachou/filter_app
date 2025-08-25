
# Web Filter App

This project is a FastAPI-based web application that allows users to upload media files (videos, photos) and filter files (`.cube` format), and then apply those filters to the media. The filtering process itself is a placeholder for a CPU-intensive task, simulated with a `time.sleep()`.

## Features

- **User Authentication**: JWT-based authentication to protect endpoints.
- **Media Uploads**: Authenticated users can upload media files.
- **Filter Uploads**: Authenticated users can upload `.cube` filter files.
- **Processing Simulation**: Apply a filter to media, simulating a long-running task.
- **File-based Database**: A simple JSON file acts as the database for metadata.

## Project Structure

```
/filter_app
├── main.py                 # App entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── /routers                # API endpoint definitions
│   ├── auth.py
│   ├── media.py
│   ├── filters.py
│   └── process.py
├── /models                 # Pydantic schemas
│   └── schemas.py
├── /utils                  # Utility modules
│   └── database.py
└── /storage                # Uploaded and processed files
    ├── media_uploads/
    ├── filter_uploads/
    └── processed_output/
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- `pip` for package installation

### Installation Steps

1.  **Clone the repository (or download the source code).**

2.  **Navigate to the project directory:**
    ```bash
    cd filter_app
    ```

3.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure your environment:**
    - The `.env` file is pre-configured with a default secret key.
    - **For production, you must change `SECRET_KEY` to a new, securely generated random string.**

### Running the Application

With your virtual environment activated and dependencies installed, run the application using Uvicorn:

```bash
uvicorn main:app --reload
```

The `--reload` flag enables hot-reloading, which is useful for development.

The API will be accessible at `http://127.0.0.1:8000`.

## API Usage

Interactive API documentation is available at `http://127.0.0.1:8000/docs` (Swagger UI) and `http://127.0.0.1:8000/redoc` (ReDoc).

### 1. Get an Authentication Token

- **Endpoint**: `POST /auth/token`
- **Request Body**: Send `username` and `password` as form data.
- **Hardcoded Users**:
    - `username`: `user1`, `password`: `fake_password_1`
    - `username`: `user2`, `password`: `fake_password_2`

**Example (`curl`):**
```bash
curl -X POST -d "username=user1&password=fake_password_1" http://127.0.0.1:8000/auth/token
```

This will return an `access_token`.

### 2. Access Protected Endpoints

For all other endpoints, include the token in the `Authorization` header:

```bash
Authorization: Bearer <your_access_token>
```

### 3. Upload a Media File

- **Endpoint**: `POST /media/upload`
- **Request Body**: `multipart/form-data` with a file.

**Example (`curl`):**
```bash
curl -X POST -H "Authorization: Bearer <token>" \
     -F "file=@/path/to/your/video.mp4" \
     http://127.0.0.1:8000/media/upload
```

### 4. Upload a Filter File

- **Endpoint**: `POST /filters/upload`
- **Request Body**: `multipart/form-data` with a `.cube` file.

**Example (`curl`):**
```bash
curl -X POST -H "Authorization: Bearer <token>" \
     -F "file=@/path/to/your/filter.cube" \
     http://127.0.0.1:8000/filters/upload
```

### 5. Apply a Filter

- **Endpoint**: `POST /process/`
- **Request Body**: JSON with `media_id` and `filter_id`.

**Example (`curl`):**
```bash
curl -X POST -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"media_id": "<your_media_id>", "filter_id": "<your_filter_id>"}' \
     http://127.0.0.1:8000/process/
```

This will trigger the simulated 10-second processing task.

