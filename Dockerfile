FROM python:3.12-alpine

LABEL maintainer="evanhugues@proton.me"
LABEL version="1.0"

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    linux-headers \
    netcat-openbsd \
    postgresql-client \
    postgresql-dev \
    wget \
    curl \
    && pip install --upgrade pip
    
ARG ENV=production
ARG FLASK_APP=app.py
ARG SERVER_PORT=5000
ARG SERVER_HOST=0.0.0.0
ARG WORKERS=3

ENV API_ENV=$ENV \
    FLASK_APP=$FLASK_APP \
    SERVER_PORT=${SERVER_PORT} \
    SERVER_HOST=${SERVER_HOST} \
    WORKERS=${WORKERS} \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

RUN mkdir -p /app/public/uploads

COPY routes/ /app/routes/
COPY sql/ /app/sql/
COPY templates/ /app/templates/
COPY *.py /app/
COPY openapi.yml /app/

RUN addgroup -g 1001 -S appgroup && \
    adduser -S -D -H -u 1001 -h /app -s /sbin/nologin -G appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE ${SERVER_PORT}

# healthcheck peut etre overridé par le compose
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/health || exit 1

# entrypoint -> init & migration de la db
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --workers ${WORKERS} --timeout 60 --bind ${SERVER_HOST}:${SERVER_PORT} ${FLASK_APP%%.py}:app"]
