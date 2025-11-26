FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------------------------------------------
# 1. INSTALL SSH & DEPENDENCIES
# ----------------------------------------------------------------
# We add 'openssh-server' here so Azure can connect.
# We sets the root password to 'Docker!' (Azure requirement).
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    openssh-server \
    && echo "root:Docker!" | chpasswd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# ----------------------------------------------------------------
# 2. CONFIGURE SSH & ENTRYPOINT
# ----------------------------------------------------------------
# Copy the ssh config file you made
COPY sshd_config /etc/ssh/

# Copy the script you made and make it runnable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ----------------------------------------------------------------
# 3. RUN
# ----------------------------------------------------------------
# Open Web Port (8000) AND SSH Port (2222)
EXPOSE 8000 2222

# Use the script to start everything
ENTRYPOINT ["/app/entrypoint.sh"]
