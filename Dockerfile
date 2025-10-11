FROM python:3.12-slim-bookworm

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./version.txt /code/version.txt

COPY ./public/uploads/default.jpg /code/public/uploads/default.jpg

COPY ./mqtt /code/mqtt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
