# Professional Color Grading Web Application

<div align="center">

![Project Banner](https://img.shields.io/badge/AWS-Cloud_Native-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production-success?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue?style=for-the-badge)

**A production-grade, cloud-native web application for applying professional color grading filters (LUTs) to images and videos**

[Live Demo](https://webfilterapp.cab432.com) • [Architecture](#architecture) • [Tech Stack](#tech-stack)

</div>

---

## Overview

A scalable web application that enables users to upload media or discover images from Pexels, then apply professional-grade color grading filters. Built with a microservices architecture on AWS, featuring auto-scaling workers, serverless functions, and comprehensive monitoring.

### Key Features

- **Professional Color Grading** - Apply industry-standard LUT filters to images and videos
- **Secure Authentication** - AWS Cognito with MFA and Google sign-in
- **Pexels Integration** - Search and import high-quality stock images
- **Asynchronous Processing** - Queue-based architecture for CPU-intensive tasks
- **Auto-Scaling** - Dynamic worker scaling based on queue depth and CPU metrics
- **Real-time Monitoring** - Custom CloudWatch metrics and dashboards
- **Production-Ready** - HTTPS, load balancing, and health checks

---

## Architecture

<img width="1190" height="493" alt="image" src="https://github.com/user-attachments/assets/e3443f6a-f3c3-4c17-88f0-a4031e96f10d" />


### Architecture Diagram

```
┌─────────────┐
│  Route 53   │  ← DNS with health checks
└──────┬──────┘
       │
┌──────▼──────────────────┐
│ Application Load        │  ← HTTPS termination (ACM)
│ Balancer                │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│  EC2 Instance           │
│  ┌──────────────────┐   │
│  │ Nginx (Routing)  │   │  ← Path-based routing
│  ├──────────────────┤   │
│  │ React Frontend   │   │  ← SPA
│  ├──────────────────┤   │
│  │ FastAPI Backend  │   │  ← REST API + JWT validation
│  └──────────────────┘   │
└──────┬──────────────────┘
       │
       ├────────────────────────────┐
       │                            │
┌──────▼──────┐            ┌────────▼────────┐
│ Amazon SQS  │            │  Amazon S3      │  ← Pre-signed URLs
│ (Job Queue) │            │  (Media Store)  │     Multipart upload
└──────┬──────┘            └─────────────────┘
       │                            ▲
┌──────▼──────────────┐             │
│ ECS on Fargate      │             │
│ ┌────────────────┐  │             │
│ │ Worker Task 1  │──┼─────────────┘
│ ├────────────────┤  │
│ │ Worker Task 2  │  │  ← FFmpeg + LUT processing
│ ├────────────────┤  │     Auto-scales based on:
│ │ Worker Task N  │  │     - Queue length
│ └────────────────┘  │     - CPU utilization
└─────────────────────┘
       │
┌──────▼──────────────┐
│ DynamoDB            │  ← Job metadata & state
│ + ElastiCache       │  ← Filter names cache
└─────────────────────┘
       │
┌──────▼──────────────┐
│ CloudWatch          │  ← Monitoring & custom metrics
│ + Lambda            │  ← S3 event triggers
└─────────────────────┘
```

### Microservices Architecture

**1. Web/API Service (EC2)**
- **Frontend**: React SPA with Vite
- **Backend**: FastAPI REST API
- **Routing**: Nginx (path-based: `/` → frontend, `/api` → backend)
- **Responsibilities**:
  - User authentication (JWT validation)
  - Media metadata management
  - Job creation and status tracking
  - Pexels API integration

**2. Media Processing Service (ECS Fargate)**
- **Workers**: Containerized Python workers
- **Processing**: FFmpeg with LUT color grading
- **Communication**: SQS long-polling
- **Scaling**: Auto-scales based on queue metrics

**3. Serverless Monitoring (Lambda)**
- **Triggers**: S3 upload/download events
- **Metrics**: Custom CloudWatch metrics for queue length
- **Auto-scaling**: Triggers ECS task scaling based on thresholds

### Data Flow

1. **Upload** → User uploads media directly to S3 via pre-signed URLs
2. **Job Creation** → Backend creates job record in DynamoDB and enqueues to SQS
3. **Processing** → ECS workers poll SQS, process media with FFmpeg, upload results to S3
4. **Status Updates** → Workers update DynamoDB; users poll for status (cached in ElastiCache)
5. **Download** → Users download processed media directly from S3 via pre-signed URLs

---

## Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Language**: JavaScript/JSX
- **Build Tool**: Vite (fast HMR)

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT validation (AWS Cognito tokens)
- **API Documentation**: Auto-generated OpenAPI/Swagger

### Worker Service
- **Runtime**: Python
- **Media Processing**: FFmpeg with LUT filters
- **Queue**: AWS SQS long-polling

### Infrastructure (AWS)
- **Compute**: 
  - EC2 (t3.medium) for web/API
  - ECS on Fargate for workers
- **Storage**: S3 (media files)
- **Database**: DynamoDB (on-demand, job metadata)
- **Cache**: ElastiCache for Memcached
- **Queue**: SQS (job distribution)
- **Auth**: Cognito (MFA + Google federated sign-in)
- **Load Balancing**: Application Load Balancer
- **DNS**: Route 53 with health checks
- **Monitoring**: CloudWatch + Lambda
- **Serverless**: Lambda (S3 event processing)
- **Security**: ACM (SSL/TLS certificates), Secrets Manager

### DevOps
- **Containerization**: Docker, Docker Compose
- **Registry**: Amazon ECR
- **Orchestration**: Amazon ECS
- **Web Server**: Nginx (reverse proxy)

---

## Key Technical Features

### 1. **Auto-Scaling Architecture**
- **ECS Workers**: Scale based on custom CloudWatch metrics
- **Trigger**: Queue length ≥ 10 → scale out; < 3 → scale in
- **CPU-Based**: Additional scaling based on worker CPU utilization
- **Lambda Integration**: S3 events trigger metric updates for real-time scaling

### 2. **Optimized Media Handling**
- **Direct S3 Access**: Pre-signed URLs bypass API server for uploads/downloads
- **Multipart Upload**: Large file support with resumable uploads
- **Range Requests**: Stream specific byte ranges for efficient delivery

### 3. **High Availability**
- **Load Balancer**: Application Load Balancer with health checks
- **Auto-Recovery**: Route 53 health checks remove unhealthy instances
- **HTTPS**: ACM-managed certificates with automatic renewal
- **Domain**: Custom domain with HTTPS (webfilterapp.cab432.com)

### 4. **Security**
- **Authentication**: AWS Cognito with MFA and Google OAuth
- **Authorization**: JWT-based API access control
- **Network**: Private subnets for workers, security groups
- **Secrets**: AWS Secrets Manager for sensitive credentials
- **TLS**: End-to-end encryption with HTTPS

### 5. **Monitoring & Observability**
- **Custom Metrics**: Queue length, processing time, success rates
- **CloudWatch Logs**: Centralized logging for all services
- **Alarms**: Automated alerts for scaling and failures
- **Dashboard**: Real-time system health visualization

---

## Project Structure

```
.
├── backend/              # FastAPI application
│   ├── main.py          # API routes and business logic
│   ├── worker_main.py   # SQS message dispatcher
│   └── requirements.txt
├── frontend/            # React + Vite SPA
│   ├── src/
│   └── package.json
├── media_worker/        # ECS worker service
│   ├── worker.py        # FFmpeg + LUT processing
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/               # Reverse proxy config
│   └── nginx.conf
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production deployment
└── build-and-push.sh          # ECR image deployment
```

---

## Deployment

### Production Architecture
- **Region**: ap-southeast-2 (Sydney)
- **Domain**: webfilterapp.cab432.com
- **SSL**: ACM Certificate (ID: 4850c62c-26d1-41d6-a260-9aab925c3452)
- **Compute**: 
  - EC2 Instance: i-0db71af932bc596a7
  - ECS Cluster: n11696630
- **Container Registry**: ECR (3 repositories: frontend, backend, nginx)

### Infrastructure Components
- **Load Balancer**: n11696630 (Application Load Balancer)
- **Auto Scaling**: ECS Service auto-scaling based on custom metrics
- **Queue**: SQS queue for job distribution
- **Lambda**: S3 event processor for metrics

---

## Cost Optimization

**Estimated Monthly Cost**: ~$168/month for ~50 concurrent users

### Cost Breakdown
- **Compute**: EC2 ($40) + ECS Fargate ($34) = $74
- **Storage**: S3 ($15) + DynamoDB ($15) = $30
- **Network**: ALB ($18) + ElastiCache ($15) = $33
- **Monitoring**: CloudWatch ($5)
- **Other**: Route 53, SQS, ACM (~$1)

### Optimization Strategies
- On-demand DynamoDB pricing for variable load
- Auto-scaling workers (only run when needed)
- S3 Lifecycle policies for archival
- ElastiCache for reduced database reads
- Pre-signed URLs for direct S3 access (no egress through EC2)

---

## Sustainability Considerations

1. **Efficient Resource Usage**
   - Cache-first architecture (Memcached → DynamoDB → S3)
   - Right-sized compute instances
   - Auto-scaling based on actual demand

2. **Optimized Data Transfer**
   - Pre-signed URLs for direct S3 access
   - WebP/AVIF for images, optimized video encoding
   - Range requests for partial file downloads

3. **Lifecycle Management**
   - S3 Lifecycle policies for archival
   - DynamoDB TTL for stale data
   - Automated cleanup of unused resources

---

## Security Features

- **Authentication**: Cognito with MFA and Google federated sign-in
- **Authorization**: JWT-based access control
- **Network Security**: Private subnets, security groups, NACLs
- **Data Encryption**: TLS in transit, S3 server-side encryption
- **Secrets Management**: AWS Secrets Manager
- **Least Privilege**: IAM roles with minimal permissions
- **HTTPS Only**: ACM-managed certificates

---

## Performance Metrics

- **Auto-Scaling**: Queue length ≥ 10 triggers scale-out
- **Worker Efficiency**: ~60% average CPU utilization
- **Cache Hit Ratio**: Optimized with ElastiCache
- **API Response Time**: Sub-second for cached reads
- **Processing Throughput**: ~100 jobs/day with auto-scaling

---

## Local Development

```bash
# Clone repository
git clone <repository-url>
cd filter-app

# Create environment file
cp .env.example .env

# Start all services with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Key Achievements

- Microservices Architecture - Decoupled, scalable services
- Container Orchestration - ECS with Fargate
- Auto-Scaling - Custom CloudWatch metrics + Lambda
- Load Distribution - Application Load Balancer
- Serverless Functions - Lambda for S3 event processing
- Communication Mechanisms - SQS for async processing
- HTTPS & Custom Domain - Production-ready security
- High Availability - Health checks and auto-recovery
- Cost Optimization - Right-sized resources, caching strategy

---


## License

This project was developed as part of CAB432 Cloud Computing coursework.

---

<div align="center">

**Built with AWS Cloud**

</div>
