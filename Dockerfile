FROM python:3.9-slim

WORKDIR /app

# Install uv provided by the astral-sh/uv Docker image or just pip install it
# Using the method recommended for adding uv to a python image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency definition
COPY pyproject.toml .

# Install dependencies using uv
# --system installs into the system python environment, avoiding virtualenv overhead in Docker
RUN uv pip install --system -r pyproject.toml

# Copy source code
COPY . .

# Create data directory
RUN mkdir -p data

# Run the application
CMD ["python", "-u", "main.py"]
