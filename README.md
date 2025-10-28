# Web Filter App

## Architecture Overview

This is a cloud-native, full-stack web application designed for applying visual filters to images and videos. It uses a decoupled architecture to ensure scalability and efficient handling of CPU-intensive tasks.

The system is composed of three core services:
-   **Frontend**: A React single-page application providing the user interface for media uploads, filter selection, and library management.
-   **Backend**: A Python FastAPI server that manages user authentication, API requests, media metadata, and dispatches processing jobs to a queue.
-   **Media Worker**: A dedicated, containerized Python worker that performs the CPU-intensive filter application.

This application is designed for and deployed on AWS:
-   The **Frontend** and **Backend** services are hosted on an **AWS EC2** instance.
-   The **Media Worker** is deployed as a container managed via **Amazon ECR**. It automatically scales based on demand.
-   Communication between the backend and the worker is handled by **AWS SQS (Simple Queue Service)**. The backend places jobs in a queue, and the workers use long-polling to fetch and process them.

## Features

-   **User Authentication**: Secure JWT-based login and session management.
-   **Cloud-Native Architecture**: Decoupled services using SQS for resilient, scalable processing.
-   **Auto-Scaling Workers**: The media processing workers in ECR scale automatically to handle fluctuating loads.
-   **Media Upload & Filtering**: Supports common image and video formats and applies `.cube` LUT filters.
-   **Pexels API Integration**: Search and import high-quality images directly from Pexels.
-   **Personal Media Library**: View, download, and manage your media files.

## Tech Stack

-   **Frontend**: JavaScript, React, Vite
-   **Backend**: Python, FastAPI
-   **Worker**: Python
-   **Queueing**: AWS SQS
-   **Containerization**: Docker, Docker Compose
-   **Cloud Hosting**: AWS EC2, AWS ECR
-   **Web Server**: Nginx

## Project Structure

The repository is organized into the three main components of the application:

```
.
├── backend/         # FastAPI application, API logic, and SQS message dispatching
├── frontend/        # React + Vite user interface
├── media_worker/    # Asynchronous worker for consuming SQS messages and processing media
├── nginx/           # Nginx configuration for reverse proxy
├── infra.yaml       # Infrastructure-as-Code template (e.g., CloudFormation, CDK)
├── docker-compose.yml      # Docker Compose for LOCAL development
└── ... and other configuration files
```

---

## Local Development Setup

Use this method to run the application on your local machine.

### Method 1

**Prerequisites:**
- Docker & Docker Compose

**Steps:**

1.  **Create Environment File**:
    Copy the example environment file. The default values are suitable for local development.
    ```bash
    cp .env.example .env
    ```

2.  **Build and Run Containers**:
    From the project root directory, run:
    ```bash
    docker-compose up --build
    ```
    The first build may take a few minutes.

3.  **Access the Application**:
    -   **Frontend**: `http://localhost:5173`
    -   **Backend API**: `http://localhost:8000`
    -   **API Docs (Swagger UI)**: `http://localhost:8000/docs`


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

---

## Production Deployment on AWS

This guide outlines how to deploy the application to an AWS EC2 instance using Docker and AWS ECR.

### Step 1: Prerequisites

-   An AWS account.
-   **AWS CLI** installed and configured on your local machine.
-   **Docker** installed on your local machine and on the EC2 server.
-   Three **AWS ECR repositories** created with the following names:
    -   `filter-app-backend`
    -   `filter-app-frontend`
    -   `filter-app-nginx`

### Step 2: Log in to AWS ECR

On your **local machine**, authenticate the Docker CLI with your Amazon ECR registry.

```bash
# Log in to AWS (e.g., using SSO)
aws sso login

# Get login password and pipe it to Docker login
aws ecr get-login-password --region <your-aws-region> | docker login --username AWS --password-stdin <your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com


```
*Replace `<your-aws-region>` and `<your-aws-account-id>` with your specific details.*

### Step 3: Build and Push Docker Images

The provided script builds multi-platform images and pushes them to ECR.

1.  **Verify Script**: Ensure the AWS Account ID and region in `build-and-push.sh` match yours.
2.  **Run the Script**:
    ```bash
    chmod +x build-and-push.sh
    ./build-and-push.sh
    ```
    This will build and push the `backend`, `frontend`, and `nginx` images to your ECR repositories.

### Step 4: Server-Side Setup (on EC2)

1.  **Connect to your EC2 instance**:
    ```bash
    ssh -i /path/to/your-key.pem ubuntu@<your-ec2-ip>
    ```

2.  **Create a project directory**:
    ```bash
    mkdir filter-app && cd filter-app
    ```

3.  **Create the `.env` file**:
    Create a `.env` file with your production environment variables.
    ```bash
    nano .env
    ```
    

4.  **Create / `docker-compose.prod.yml` **：
    This file pulls the images from ECR.
    ```bash
    nano docker-compose.prod.yml
    ```
    Paste the following content into the file. **Remember to replace the AWS Account ID and region with your own.**

    ```yaml
    # docker-compose.prod.yml 
    version: '3.8'

services:
  backend:
    image: 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-backend:latest
    env_file:
      - ./.env
    environment:
      USE_FAKE_SQS: "false"
      USE_FAKE_PROCESSING_JOBS: "false"
    restart: always

  processor-worker:
    image: 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-backend:latest
    command: ["python", "worker_main.py"]
    env_file:
      - ./.env
    environment:
      USE_FAKE_SQS: "false"
      USE_FAKE_PROCESSING_JOBS: "false"
    depends_on:
      - backend
    restart: always

  frontend:
    image: 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-frontend:latest
    restart: always

      nginx:
        image: 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-nginx:latest
    ports:
      - "80:80" 
    restart: always
    depends_on:
      - backend
      - processor-worker
      - frontend
    ```

    

### Step 5: Launch the Application on EC2

1.  **Pull the latest images**:
    ```bash
    docker-compose -f docker-compose.prod.yml pull
    ```

2.  **Start the services**:
    ```bash
    docker-compose -f docker-compose.prod.yml up -d --build
    ```

3.  **Access and Verify**:
    The application should now be accessible via your EC2 instance's public IP address on port 80. Nginx serves the frontend and forwards API requests to the backend.

    - **Application URL**: `http://<your-ec2-ip>`
    - **API Docs URL**: `http://<your-ec2-ip>/docs`

    You can check the logs to ensure everything is running correctly:
    ```bash
    # Backend API 日誌
    docker-compose -f docker-compose.prod.yml logs -f backend

    # Worker 任務處理日誌
    docker-compose -f docker-compose.prod.yml logs -f processor-worker
    ```


docker-compose -f docker-compose.prod.yml down --remove-orphans
docker system prune -f
docker-compose -f docker-compose.prod.yml up -d --build
