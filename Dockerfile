FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# Create a directory for Supervisor config
RUN mkdir -p /etc/supervisor/conf.d

# Set the working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the port the web server listens on
EXPOSE 8000

# Supervisor will start both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 