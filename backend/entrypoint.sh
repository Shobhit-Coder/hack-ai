#!/bin/sh
set -e

# 1. Start the SSH service in the background
echo "Starting SSH..."
service ssh start

# 2. Run Database Migrations
echo "Running Migrations..."
python manage.py migrate

# 3. Collect Static Files
echo "Collecting Static Files..."
python manage.py collectstatic --noinput

# 4. Create Admin User (if it doesn't exist)
echo "Checking for Admin User..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'HackathonPassword123!')"

# 5. Start the Server (Gunicorn)
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 interview_ai.wsgi
