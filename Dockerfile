FROM python:3.9.13-slim-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY api /var/api

WORKDIR /var/api

RUN pip3 install psycopg2-binary

RUN pip3 install -r /var/api/requirements-dev.txt

CMD ["python", "-m", "app.app"]