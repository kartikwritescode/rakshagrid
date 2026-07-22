# backend/fastapi/Dockerfile
FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/fastapi/requirements.txt /workspace/backend/fastapi/requirements.txt
RUN pip install --no-cache-dir -r backend/fastapi/requirements.txt

# Copy entire repository
COPY . /workspace

ENV PYTHONPATH=/workspace
EXPOSE 8000

CMD ["uvicorn", "backend.fastapi.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
