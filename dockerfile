# Stage 1: Build
FROM python:3.11-slim AS builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Install poetry or pip if needed
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy Python dependencies from the builder stage
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy the FastAPI application code
COPY . .

# Expose the application port
EXPOSE 8000

# Set the entry point for the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
