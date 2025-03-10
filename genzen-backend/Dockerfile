
# Base image
FROM python:3.13-alpine AS base

# Set working directory
WORKDIR /app

# Update and install poetry
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev cargo && \
    # pip install --upgrade pip && \
    pip install poetry && \
    apk del gcc musl-dev libffi-dev python3-dev openssl-dev && \
    rm -rf /var/cache/apk/*

# Copy poetry declarative instruction files
COPY pyproject.toml poetry.lock ./

# Create virtual env and set its path
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies
RUN python -m venv venv && \
    . /app/venv/bin/activate && \
    poetry install --no-root --only main && \
    rm -rf /var/cache/apk/*
# Copy application code
COPY . .

# Runtime stage
FROM python:3.13-alpine AS runtime

# Set working directory
WORKDIR /app

# Copy the application code from base 
COPY --from=base /app /app

# Ensure the virtual environment is set
ENV PATH="/app/venv/bin:$PATH"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]