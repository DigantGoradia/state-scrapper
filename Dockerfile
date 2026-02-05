FROM python:3.12-slim-bookworm

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install dependencies
# Copy only pyproject.toml and uv.lock (if it exists) first to leverage cache
COPY pyproject.toml .
# COPY uv.lock . # Uncomment if/when uv.lock is committed and useful

# Install dependencies into the system python since we are in a container
# using cache mount for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r pyproject.toml

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copy source code
COPY . .

# Ensure data directory exists and is writable by appuser if needed
# (Doing this before switching user or adjusting permissions)
USER root
RUN mkdir -p data && chown -R appuser /app/data
USER appuser

# Correct entrypoint for src layout
CMD ["python", "-m", "src.main"]
