FROM python:3.12-slim

LABEL maintainer="Karim"
LABEL description="Prague Real Estate ML API"
LABEL version="1.0"

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

COPY . .

COPY crontab /etc/cron.d/prague-realty
RUN chmod 0644 /etc/cron.d/prague-realty && \
    crontab /etc/cron.d/prague-realty


RUN touch /var/log/cron.log

RUN mkdir -p /app/data /app/models

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD cron && uvicorn src.main:app --host 0.0.0.0 --port 8000