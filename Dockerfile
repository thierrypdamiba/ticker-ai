# Stage 1: Build the application
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Stage 2: Create a minimal runtime image
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/bot.py .
COPY --from=builder /app/momentum_strategy.py .
COPY --from=builder /app/robinhood_client.py .
COPY --from=builder /app/utils.py .

# Copy any other necessary files/directories (e.g., config files)
# COPY --from=builder /app/config ./config

# Install any runtime dependencies (if different from build dependencies)
RUN apt-get update && apt-get install --no-install-recommends -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (if any, ideally minimal)
# RUN pip install --no-cache-dir some-lightweight-dependency

# Set environment variables (example)
ENV PYTHONUNBUFFERED=1

# Expose any necessary ports (if applicable)
# EXPOSE 8080

# Define the entry point for the application
ENTRYPOINT ["python", "bot.py"]