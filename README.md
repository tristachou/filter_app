# Web Filter App

## Project Overview

This is a full-stack web application that allows users to upload images and videos, apply custom filters (Look-Up Tables - LUTs), and download the processed media. It features a user authentication system, integration with the Pexels API for sourcing images, and a personal media library for each user.

The entire application is containerized with Docker for consistent development and production environments.

## Features

-   **User Authentication**: Secure JWT-based login and session management.
-   **Media Upload**: Supports common image (JPG, PNG) and video (MP4, MOV) formats.
-   **LUT Filter Application**: Apply `.cube` LUT filters to uploaded media using `ffmpeg`.
-   **Pexels API Integration**: Search for and import high-quality images directly from Pexels.
-   **Personal Media Library**: View, download, and manage your uploaded and processed files.
-   **Containerized**: Fully containerized with Docker and Docker Compose for easy setup.
-   **RESTful API**: A well-defined FastAPI backend serving a modern React frontend.

## Tech Stack

-   **Backend**: Python, FastAPI
-   **Frontend**: JavaScript, React, Vite
-   **Web Server/Proxy**: Nginx
-   **Containerization**: Docker, Docker Compose
-   **Deployment**: AWS ECR (Elastic Container Registry)

## Project Structure

```
.
├── backend/         # FastAPI application, API logic, and media processing
├── frontend/        # React + Vite user interface
├── nginx/           # Nginx configuration and Dockerfile
├── build-and-push.sh # Script to build and push Docker images to AWS ECR
├── docker-compose.yml      # Docker Compose for LOCAL development
└── docker-compose.prod.yml # Docker Compose for PRODUCTION deployment
```

---

## Local Development Setup

Use this method to run the application on your local machine.

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
    Paste your production secrets (e.g., `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`).

4.  **Create the `docker-compose.prod.yml` file**:
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
          - frontend
    ```

### Step 5: Launch the Application on EC2

1.  **Pull the latest images**:
    ```bash
    docker-compose -f docker-compose.prod.yml pull
    ```

2.  **Start the services**:
    ```bash
    docker-compose -f docker-compose.prod.yml up -d
    ```

3.  **Access and Verify**:
    The application should now be accessible via your EC2 instance's public IP address on port 80. Nginx serves the frontend and forwards API requests to the backend.

    - **Application URL**: `http://<your-ec2-ip>`
    - **API Docs URL**: `http://<your-ec2-ip>/docs`

    You can check the logs to ensure everything is running correctly:
    ```bash
    # Check logs for a specific service (e.g., backend)
    docker-compose -f docker-compose.prod.yml logs -f backend
    ```
