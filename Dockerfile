FROM python:3.12-slim

WORKDIR /api

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY migrations migrations/
COPY models.py extensions.py app.py wsgi.py ./
COPY routes routes/
COPY static static/
COPY templates templates/
COPY openapi.yml ./

COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Environment will be provided by docker-compose
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "--timeout=120", "wsgi:app"]