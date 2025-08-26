# Web Filter App

## Project Description

This is a web application that allows users to upload images and videos, apply custom filters (Look-Up Tables - LUTs) to them, and then download the processed media. It features a user authentication system, enabling each user to manage their own library of uploaded and processed media.

## Features

-   **User Authentication**: Secure login and session management using JWT.
-   **Media Upload**: Upload images (JPG, PNG) and videos (MP4, MOV, AVI, MKV).
-   **Filter Application**: Apply pre-defined or custom `.cube` LUT filters to uploaded media.
-   **CPU-Intensive Processing**: Utilizes `ffmpeg` for media processing, which can be CPU-intensive, especially for video files.
-   **Media Library**: View, download, and clear a personal library of processed media.
-   **RESTful API**: A clear and well-defined RESTful API as the primary interface.
-   **Web Client**: A responsive web-based client accessible via a browser, interacting with all API endpoints.

## Architecture

The project is structured as a Single-Page Application (SPA) with a Python FastAPI backend and a vanilla JavaScript frontend.

### Backend (FastAPI)

-   **`main.py`**: The main entry point, setting up the FastAPI application and including API routers.
-   **`routers/`**: Contains modular API endpoints for `auth`, `media`, `filters`, and `process`.
-   **`models/schemas.py`**: Defines Pydantic models for data validation and serialization.
-   **`utils/database.py`**: A simple JSON-based database (`db.json`) for storing user, media, and filter metadata.
-   **`services/process_media.py`**: Handles the core media processing logic using `ffmpeg`.
-   **`storage/`**: Stores uploaded raw media, filter files, and processed output.

### Frontend (Vanilla JavaScript)

-   **`public/index.html`**: The main HTML structure for the application.
-   **`public/script.js`**: Contains the core JavaScript logic for UI interaction, API communication, and state management, organized into modular components.
-   **`public/style.css`**: Provides the styling for the application.

## Prerequisites

Before you begin, ensure you have the following installed:

-   **Python 3.9+**
-   **pip** (Python package installer)
-   **Node.js & npm** (for frontend dependencies, though not strictly used for build process in vanilla JS)
-   **ffmpeg**: Essential for media processing. Ensure it's installed and accessible in your system's PATH.
    -   *For Ubuntu/Debian*: `sudo apt update && sudo apt install ffmpeg`
    -   *For macOS (using Homebrew)*: `brew install ffmpeg`
    -   *For Windows*: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.
-   **Docker** (if you plan to run the application via Docker containers)

## Setup & Running Locally

Follow these steps to set up and run the application on your local machine:

1.  **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd SimpleGrading/filter_app
    ```

2.  **Create a Python virtual environment** (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the FastAPI backend**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The backend API will be accessible at `http://localhost:8000/api`.

5.  **Access the Frontend**: Open your web browser and navigate to `http://localhost:8000`.

    *Default Login Credentials (for initial setup)*:
    -   Username: `user1`
    -   Password: `fake_password_1`

## Docker Setup

To run the application using Docker:

1.  **Build the Docker image**:
    Navigate to the project root directory (where `Dockerfile` is located) and run:
    ```bash
    docker build -t web-filter-app .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run -p 8000:8000 web-filter-app
    ```
    The application will be accessible at `http://localhost:8000`.

## Usage

1.  **Login**: Use the default credentials to log in.
2.  **Upload Media**: Click or drag-and-drop an image or video file into the designated area.
3.  **Apply Filter**: Select a filter from the bar at the bottom. The application will process the media.
4.  **Download Result**: Once processing is complete, download the filtered media.
5.  **My Library**: Access your personal media library from the top right corner to view and download previously processed files, or clear your library.

## Assignment Criteria Status

Here's an assessment of the project's current status against the provided assignment criteria:

### Core criteria (20 marks)

-   [x] **CPU Intensive task (3 marks)**
    -   Uses at least one CPU intensive process (ffmpeg for media processing).
    -   *Needs verification*: Exceeding 80% CPU usage for an extended time depends on media size and system specs, requires load testing.
-   [ ] **CPU load testing (2 marks)**
    -   *Missing*: A dedicated script or manual method for generating server load.
-   [x] **Data types (3 marks)**
    -   Stores media files (images/videos), filter files (.cube), and metadata in JSON (db.json).
-   [ ] **Containerize the app (3 marks)**
    -   *Missing*: Docker image is built, but deployment to AWS ECR/EC2 is not part of this setup.
-   [ ] **Deploy the container (3 marks)**
    -   *Missing*: Deployment to AWS ECR/EC2 is not part of this setup.
-   [x] **REST API (3 marks)**
    -   Application has a clear REST-based API as its primary interface.
-   [x] **User login (3 marks)**
    -   Basic user login and session management with JWT, with distinctions for different users.

### Additional criteria (10 marks)

-   [ ] **Extended API features (2.5 marks)**
    -   *Missing*: Features like versioning, pagination, filtering, or sorting are not implemented.
-   [ ] **External APIs (2.5 marks)**
    -   *Missing*: The application does not use any external APIs.
-   [x] **Additional types of data (2.5 marks)**
    -   Handles various media formats (image/video) and LUT files, demonstrating diverse data handling and manipulation.
-   [x] **Custom processing (2.5 marks)**
    -   Significant custom processing implemented in the CPU-intensive media filtering (ffmpeg command construction and integration).
-   [ ] **Infrastructure as code (2.5 marks)**
    -   *Missing*: While Dockerfile is provided, extensive use of IaC tools like Docker Compose, CloudFormation, or CDK is not present.
-   [x] **Web client (2.5 marks)**
    -   Includes a web client that interfaces with all implemented API endpoints.