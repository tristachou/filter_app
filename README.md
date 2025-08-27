# Web Filter App

## Project Description

This is a web application that allows users to upload images and videos, apply custom filters (Look-Up Tables - LUTs) to them, and then download the processed media. It features a user authentication system, enabling each user to manage their own library of uploaded and processed media.

## Features

-   **User Authentication**: Secure login and session management using JWT.
-   **Media Upload**: Upload images (JPG, PNG) and videos (MP4, MOV, AVI, MKV).
-   **Filter Application**: Apply pre-defined or custom `.cube` LUT filters to uploaded media.
-   **CPU-Intensive Processing**: Utilizes `ffmpeg` for media processing.
-   **Media Library**: View, download, and clear a personal library of processed media.
-   **RESTful API**: A clear and well-defined RESTful API as the primary interface.
-   **Modern Web Client**: A responsive React-based client that interacts with all API endpoints.

## Project Structure

The project has been refactored into a modern monorepo structure with a separate backend and frontend.

-   **`backend/`**: Contains the Python FastAPI application, which handles all API logic, media processing, and database interactions.
-   **`frontend/`**: Contains the React + Vite application, which serves as the user interface.
-   **`docker-compose.yml`**: Defines the services, networks, and volumes for running the entire application with Docker.
-   **`.env`**: A file (that you will create) to hold environment variables for the backend service.

## Prerequisites

Before you begin, ensure you have the following installed:

-   **Python 3.9+** & **pip** (for manual backend setup)
-   **Node.js 20+** & **npm** (for manual frontend setup)
-   **Docker** & **Docker Compose** (for the recommended setup)
-   **ffmpeg**: Essential for media processing. Ensure it's installed and accessible in your system's PATH.

## How to Run the Application

There are two ways to run the application. The recommended method for ease of use is with Docker Compose.

### Method 1: Using Docker Compose (Recommended)

This method runs both the backend and frontend in isolated Docker containers.

1.  **Set up Environment Variables**:
    Create a file named `.env` in the project root directory by copying the example file:
    ```bash
    cp .env.example .env
    ```
    *Note: The default values in this file are for development only.*

2.  **Build and Run the Containers**:
    From the project root directory, run:
    ```bash
    docker-compose up --build
    ```
    This command will build the images for both services and start them. Be patient, as the first build can take several minutes.

3.  **Access the Application**:
    -   The **Frontend** will be available at: `http://localhost:5173`
    -   The **Backend API** will be available at: `http://localhost:8000`
    -   API documentation (Swagger UI) is at: `http://localhost:8000/docs`

### Method 2: Running Services Manually (for Development)

Follow these steps to run each service in a separate terminal.

#### Running the Backend

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set environment variables**:
    The backend requires the environment variables defined in the `.env` file at the project root. You can either load them into your shell manually or run the server from the root directory. The simplest way is to ensure the `.env` file exists at the project root.

5.  **Run the FastAPI server**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

#### Running the Frontend

1.  **Navigate to the frontend directory** (in a new terminal):
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Run the Vite development server**:
    ```bash
    npm run dev
    ```
    The frontend will be accessible at `http://localhost:5173`.

## Usage

1.  **Login**: Use the default credentials (`user1` / `fake_password_1`) to log in.
2.  **Upload Media**: Click or drag-and-drop an image or video file.
3.  **Apply Filter**: Select a filter from the bar at the bottom.
4.  **Download Result**: Once processing is complete, download the filtered media.
5.  **My Library**: Access your personal media library to view, download, or clear files.

## Assignment Criteria Status

(This section is preserved from the original README for your reference)

### Core criteria (20 marks)
-   [x] **CPU Intensive task (3 marks)**
-   [ ] **CPU load testing (2 marks)**
-   [x] **Data types (3 marks)**
-   [ ] **Containerize the app (3 marks)**
-   [ ] **Deploy the container (3 marks)**
-   [x] **REST API (3 marks)**
-   [x] **User login (3 marks)**

### Additional criteria (10 marks)
-   [ ] **Extended API features (2.5 marks)**
-   [ ] **External APIs (2.5 marks)**
-   [x] **Additional types of data (2.5 marks)**
-   [x] **Custom processing (2.5 marks)**
-   [ ] **Infrastructure as code (2.5 marks)**
-   [x] **Web client (2.5 marks)**
