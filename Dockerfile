FROM python:3.14.2-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser

RUN mkdir -p /var/api && chown -R appuser:appuser /var/api

COPY --chown=appuser:appuser api/requirements.txt /var/api/

WORKDIR /var/api

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir psycopg2-binary && \
    pip3 install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser api /var/api

USER appuser

EXPOSE 5001

CMD ["python", "-m", "app.app"]
