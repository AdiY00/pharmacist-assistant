# Use Python 3.13 Alpine as the base image for building
FROM python:3.13-alpine AS builder

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /bin/

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Set the working directory
WORKDIR /app

# Copy dependency files first for better caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code and install project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Seed the database
RUN uv run python -c "from db import init_db; init_db(seed=True)"

# Final stage
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the virtual environment and necessary runtime files from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/main.py /app/chainlit.md ./
COPY --from=builder /app/agent ./agent
COPY --from=builder /app/db ./db
COPY --from=builder /app/data ./data
COPY --from=builder /app/public ./public
COPY --from=builder /app/.chainlit ./.chainlit

# Expose the default Chainlit port
EXPOSE 8080

# Command to run the application
CMD [".venv/bin/chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8080"]
