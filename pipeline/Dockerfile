FROM python:3.10-slim

# --------------------------------------------------------
# System packages for Airflow + python deps
# --------------------------------------------------------
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    libpq-dev \
    gcc \
    g++ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# Environment variables for Airflow
# --------------------------------------------------------
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=SequentialExecutor
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false
ENV AIRFLOW__CORE__LOAD_EXAMPLES=false

# --------------------------------------------------------
# Create Airflow folder + airflow user
# --------------------------------------------------------
RUN mkdir -p $AIRFLOW_HOME

RUN groupadd -g 50000 airflow && \
    useradd -u 50000 -g 50000 -d ${AIRFLOW_HOME} -s /bin/bash airflow && \
    chown -R airflow:airflow ${AIRFLOW_HOME}

# --------------------------------------------------------
# Install Python dependencies
# --------------------------------------------------------
COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# --------------------------------------------------------
# Copy project files into /app
# --------------------------------------------------------
COPY . /app
WORKDIR /app

RUN chown -R airflow:airflow /app

# --------------------------------------------------------
# Switch to airflow user
# --------------------------------------------------------
USER airflow

EXPOSE 8080
CMD ["bash"]
