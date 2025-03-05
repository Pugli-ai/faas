#!/bin/bash

# collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# handle database migrations
echo "Generating database migrations..."
python manage.py makemigrations

# apply migrations
echo "Applying database migrations..."
python manage.py migrate

# # create superuser if not exists
# python scripts/create_admin.py

# start the server
echo "Starting server..."
exec gunicorn --bind 0.0.0.0:8000 ideapools.wsgi:application --timeout 200 --worker-connections=1000 --workers=5 --access-logfile -