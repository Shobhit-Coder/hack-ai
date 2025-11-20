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

EXPOSE 8000

# --- THIS IS THE MISSING PART ---
# Replace 'your_project_name' with the name of the folder containing settings.py/wsgi.py
# Example: if you have backend/hackathon_api/wsgi.py, use "hackathon_api.wsgi"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "interview_ai.wsgi"]
