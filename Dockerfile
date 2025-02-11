# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ideapools.settings
ENV STATIC_ROOT=/app/staticfiles
ENV STATICFILES_STORAGE=django.contrib.staticfiles.storage.StaticFilesStorage

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Collect static files with simple storage backend
RUN python manage.py collectstatic --noinput --clear --no-post-process

# Run manage.py when the container launches
CMD ["uvicorn", "ideapools.asgi:application", "--host", "0.0.0.0", "--port","8000"]
