FROM python:3.12-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./version.txt /code/version.txt

COPY ./public/uploads/default.jpg /code/public/uploads/default.jpg

ARG MQTT_USER
ARG MQTT_PASSWORD

ENV MQTT_USER=${MQTT_USER} \
    MQTT_PASSWORD=${MQTT_PASSWORD}

COPY ./mqtt/entrypoint.sh /code/mqtt/entrypoint.sh
COPY ./mqtt/mosquitto.conf /code/mqtt/mosquitto.conf

RUN echo "${MQTT_USER}:${MQTT_PASSWORD}" > /code/mqtt/passwordfile

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
