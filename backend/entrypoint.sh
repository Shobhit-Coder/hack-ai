#!/bin/sh
set -e

echo "Starting SSH..."
/usr/sbin/sshd &

echo "Running Migrations..."
python manage.py migrate

echo "Collecting Static Files..."
python manage.py collectstatic --noinput

echo "Checking for Admin User..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'HackathonPassword123!')"

echo "Starting Gunicorn..."
exec gunicorn interview_ai.wsgi:application --bind 0.0.0.0:8000
