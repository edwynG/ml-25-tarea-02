FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1-dev \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required by Reflex)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

WORKDIR /usr/app
COPY . .

RUN pip install -r requirements.txt

# Initialize Reflex
RUN reflex init

EXPOSE 3000 8000

CMD ["reflex", "run", "--env", "prod"]
