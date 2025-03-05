# Here we are using a multi-stage build to reduce the size of the final image.
# Stage 1: Build Stage
FROM python:3.12 AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies in a separate layer
COPY requirements.txt /app/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production Image
FROM python:3.12 AS final

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy only necessary files from the build stage
COPY --from=builder /install /usr/local

# Copy application files
COPY . /app

# Expose port 8000
EXPOSE 8000


# Set the entrypoint for the app (using gunicorn to serve the Django app)
CMD ["/bin/bash", "entrypoint.sh"]
