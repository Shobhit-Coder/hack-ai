FROM python:3.12-slim

WORKDIR /app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install system dependencies (gcc/libpq needed for Postgres)
COPY requirements.txt .
RUN apt-get update && apt-get install -y libpq-dev gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

# ... (keep everything above the same) ...

EXPOSE 8000

# This command does EVERYTHING automatically:
# 1. Migrates database
# 2. Collects static files
# 3. Creates an admin user (Username: admin, Password: HackathonPassword123!)
# 4. Starts Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'HackathonPassword123!')\" && gunicorn --bind 0.0.0.0:8000 your_project_name.wsgi"]
