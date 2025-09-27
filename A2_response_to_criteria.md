Assignment 2 - Cloud Services Exercises - Response to Criteria
================================================

Instructions
------------------------------------------------
- Keep this file named A2_response_to_criteria.md, do not change the name
- Upload this file along with your code in the root directory of your project
- Upload this file in the current Markdown format (.md extension)
- Do not delete or rearrange sections.  If you did not attempt a criterion, leave it blank
- Text inside [ ] like [eg. S3 ] are examples and should be removed


Overview
------------------------------------------------

- **Name:** Hsin-Yu Chou
- **Student number:** N11696630
- **Partner name (if applicable):** N11789701
- **Application name:** Web Filter App
- **Two line description:** A web application that allows users to upload their media (images/videos) or discover images from Pexels, and then apply professional color grading filters (LUTs) to them.
- **EC2 instance name or ID:** i-0db71af932bc596a7

------------------------------------------------

### Core - First data persistence service

- **AWS service name:** Amazon S3
- **What data is being stored?:** User-uploaded original media files (images and videos), and the processed media files after filters have been applied.
- **Why is this service suited to this data?:** S3 is an object storage service designed for high scalability, availability, and durability. It is ideal for storing large binary files like images and videos, which are not suitable for databases.
- **Why is are the other services used not suitable for this data?:** Storing large binary files in a database (like DynamoDB or RDS) is inefficient, costly, and would quickly hit size limitations.
- **Bucket/instance/table name:** n11696630
- **Video timestamp:**00:00:00-00:20:29
- **Relevant files:**
    - backend/utils/s3_client.py
    - backend/routers/media.py
    - backend/services/process_media.py

### Core - Second data persistence service

- **AWS service name:**  Amazon DynamoDB
- **What data is being stored?:** Application metadata, such as user profiles, and a list of media files owned by each user (including file names, descriptions, and the corresponding S3 object keys).
- **Why is this service suited to this data?:** DynamoDB is a fully managed NoSQL database that provides low-latency performance at any scale. It is well-suited for storing structured metadata with simple key-value access patterns, like fetching a user's profile or their list of files by a user ID.
- **Why is are the other services used not suitable for this data?:** S3 does not support complex queries on metadata. A relational database (RDS) could work, but it might be overkill if access patterns are simple, and DynamoDB offers better serverless scaling and simpler integration for this use case.
- **Bucket/instance/table name:** 
    -n11696630-filter_items
    -n11696630-media_items
- **Video timestamp:**00:00:00-00:20:29
- **Relevant files:**
    - backend/utils/database.py
    - backend/models/schemas.py

### Third data service (not attempted)

- **AWS service name:**  
- **What data is being stored?:** 
- **Why is this service suited to this data?:** 
- **Why is are the other services used not suitable for this data?:** 
- **Bucket/instance/table name:**
- **Video timestamp:**
- **Relevant files:**
    -

### S3 Pre-signed URLs

- **S3 Bucket names:** n11696630
- **Video timestamp:**00:42:22-01:90:20
- **Relevant files:**
    - backend/utils/s3_client.py
    - backend/routers/media.py

### In-memory cache

- **ElastiCache instance name:** n11696630
- **What data is being cached?:** The list of available LUT filters, which are read from the `backend/assets/luts/` directory. Additionally, results from the external Pexels API could be cached.
- **Why is this data likely to be accessed frequently?:** The list of available filters is the same for all users and is needed every time the UI is loaded. Caching it avoids repeated filesystem reads. Caching Pexels API results for common search terms reduces external API calls, lowers latency, and helps avoid rate limiting.
- **Video timestamp:**01:90:20-01:59:16
- **Relevant files:**
    - backend/utils/cache_client.py
    - backend/routers/filters.py
    - backend/routers/pexels.py

### Core - Statelessness

- **What data is stored within your application that is not stored in cloud data services?:** Temporary files during media processing. For example, an uploaded file might be temporarily stored on the application server's local disk before it is processed and uploaded to S3.
- **Why is this data not considered persistent state?:** These are intermediate, ephemeral files. If the application instance were to stop, these files can be safely lost because they can be regenerated from the original source file. They are not the source of truth.
- **How does your application ensure data consistency if the app suddenly stops?:** The application likely follows atomic operation patterns. For instance, a new media record is created in DynamoDB only *after* the corresponding file has been successfully uploaded to S3. If the process fails midway, no inconsistent data is left behind, and the client can safely retry the operation.
- **Relevant files:**
    - backend/services/process_media.py
    - backend/routers/media.py

### Graceful handling of persistent connections (not attempted)

- **Type of persistent connection and use:** 
- **Method for handling lost connections:** 
- **Relevant files:**
    -


### Core - Authentication with Cognito

- **User pool name:** n11696630
- **How are authentication tokens handled by the client?:** After a successful login, the frontend client (React) receives JWTs (ID, access, and refresh tokens) from Cognito. These tokens are typically managed by a library like AWS Amplify and stored in the browser's `localStorage` or `sessionStorage`. Subsequent API requests to the backend include the token in the `Authorization` header for authentication.
- **Video timestamp:**01:59:16-02:37:15
- **Relevant files:**
    - backend/utils/cognito_auth.py
    - backend/routers/auth.py
    - frontend/src/cognitoAuth.js
    - frontend/src/AuthContext.jsx
    - frontend/src/components/LoginView.jsx

### Cognito multi-factor authentication

- **What factors are used for authentication:** Password (something the user knows) and a Time-based One-Time Password (TOTP) from an authenticator app (something the user has).
- **Video timestamp:**02:37:15-03:03:01
- **Relevant files:**
    - frontend/src/components/MfaSetupView.jsx
    - frontend/src/components/MfaChallengeView.jsx
    - backend/routers/auth.py

### Cognito federated identities

- **Identity providers used:** Google
- **Video timestamp:**03:03:01-03:36:05
- **Relevant files:**
    - frontend/src/components/LoginView.jsx
    - frontend/src/cognitoAuth.js

### Cognito groups

- **How are groups used to set permissions?:** Cognito Groups control filter visibility. Users in the `admin` group can upload 'public' filters, which are visible to all users. Other users can only upload 'private' filters, visible only to themselves. The backend API enforces this by checking the group claim in the user's JWT upon filter upload.
- **Video timestamp:** 03:36:05-05:05:18
- **Relevant files:**
    - backend/routers/filters.py
    - backend/utils/cognito_auth.py
    - backend/models/schemas.py

### Core - DNS with Route53

- **Subdomain**: filterapp.cab432.com
- **Video timestamp:**05:05:18-05:12:03

### Parameter store

- **Parameter names:** 
    - /n11696630/prod/COGNITO_APP_CLIENT_ID
    - /n11696630/prod/COGNITO_REGION
    - /n11696630/prod/COGNITO_USER_POOL_ID
    - /n11696630/prod/MEMCACHED_ENDPOINT
    - /n11696630/prod/S3_BUCKET_NAME
- **Video timestamp:**05:12:03-06:00:00
- **Relevant files:**
    - backend/config.py
    - backend/utils/cache_client.py
    - backend/utils/s3_client.py
    - backend/utils/cognito_auth.py

### Secrets manager

- **Secrets names:** /n11696630/prod/api_keys
- **Video timestamp:**06:00:00-06:22:09
- **Relevant files:**
    - backend/config.py
    - backend/routers/pexels.py

### Infrastructure as code

- **Technology used:** CloudFormation
- **Services deployed:** CloudFormation (infra_core.yaml) deploys two DynamoDB tables, a Cognito User Pool+App Client, SSM Parameters, and a Secrets Manager secret—each tagged with qut-username/qut-username2 for partner access. VPC/EC2/ElastiCache are excluded due to CAB432 account denies, but this still meets the IaC requirement for new services. One-command deploy/teardown (deploy.sh/destroy.sh) and the app uses Cognito for registration, (email confirmation when quota allows), and JWT login.
- **Video timestamp:**
- **Relevant files:**
    - infra.yaml
    - deploy.sh
    - destory.sh

### Other (with prior approval only)

- **Description:**
- **Video timestamp:**
- **Relevant files:**
    -

### Other (with prior permission only)

- **Description:**
- **Video timestamp:**
- **Relevant files:**
    -