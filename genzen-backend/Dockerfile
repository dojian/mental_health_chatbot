
# Base image
FROM python:3.13-slim AS base


ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.1 \
    PATH="/root/.local/bin:$PATH"

# Update and install poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Install newer Rust compiler using rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup default stable

RUN curl -sSL https://install.python-poetry.org | python3 -
        
# Set working directory
WORKDIR /app

# Configure Poetry to create virtual env in project
RUN poetry config virtualenvs.in-project true

# Copy poetry declarative instruction files
COPY pyproject.toml poetry.lock ./

# Either use an older version of pendulum or exclude it
RUN poetry install -n --no-root
# RUN poetry install

# Runtime stage
FROM python:3.13-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 

    # Install only essential runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY . .

# Copy the virtual environment from the base stage
COPY --from=base /app/.venv /app/.venv

# Set PATH to include the virtual environment binaries
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]