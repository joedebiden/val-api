FROM python:3.12-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# copy and setup of the version before building image w/ github action
COPY ./version.txt /code/version.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
