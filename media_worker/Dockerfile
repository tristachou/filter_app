FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY media_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY media_worker/main.py .
COPY media_worker/process_logic.py .
COPY media_worker/worker_schemas.py .
COPY media_worker/database_utils.py .

COPY backend/assets/luts /app/assets/luts

ENV AWS_REGION="ap-southeast-2"
ENV SQS_QUEUE_URL="https://sqs.ap-southeast-2.amazonaws.com/901444280953/n11696630"
ENV S3_BUCKET_NAME="n11696630"
ENV LUT_DIRECTORY="/app/assets/luts"

CMD ["python", "main.py"]

