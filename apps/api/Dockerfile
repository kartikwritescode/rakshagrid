# apps/api/Dockerfile
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY apps/api/requirements.txt /workspace/apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

# Copy repository
COPY . /workspace

# Install monorepo packages in editable mode
RUN pip install --no-cache-dir --no-deps -e packages/common -e packages/ai-scam -e packages/ai-currency -e packages/ai-crime -e packages/ai-graph -e apps/api

EXPOSE 8000

CMD ["uvicorn", "rakshagrid.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
