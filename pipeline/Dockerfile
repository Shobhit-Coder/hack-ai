FROM python:3.10-slim

# --------------------------------------------------------
# System packages for PDF extraction + OCR + Airflow deps
# --------------------------------------------------------
RUN apt-get update && apt-get install -y \
    bash \
    tesseract-ocr \
    poppler-utils \
    curl \
    libpq-dev \
    gcc \
    g++ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# Environment variables for Airflow
# --------------------------------------------------------
ENV AIRFLOW_HOME=/opt/airflow

# These may be overridden by docker-compose, but defaults here are fine
ENV AIRFLOW__CORE__EXECUTOR=SequentialExecutor
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false
ENV AIRFLOW__CORE__LOAD_EXAMPLES=false

# --------------------------------------------------------
# Create Airflow folder and airflow user
# --------------------------------------------------------
RUN mkdir -p $AIRFLOW_HOME

# Create airflow user with UID 50000 to match AIRFLOW_UID
RUN groupadd -g 50000 airflow && \
    useradd -u 50000 -g 50000 -d ${AIRFLOW_HOME} -s /bin/bash airflow && \
    chown -R airflow:airflow ${AIRFLOW_HOME}

# --------------------------------------------------------
# Copy requirements (pipeline + Airflow)
# --------------------------------------------------------
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# --------------------------------------------------------
# Copy your entire project inside the image
# --------------------------------------------------------
COPY . /app
WORKDIR /app

# Make sure airflow user owns project dirs that will be used
RUN chown -R airflow:airflow /app

USER airflow

# Expose Airflow webserver port
EXPOSE 8080

# Command is overridden by docker-compose, but keep bash as default
CMD ["bash"]
