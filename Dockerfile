FROM python:3.12-alpine

# upgrade pip
RUN pip install --upgrade pip

# get curl for healthchecks
RUN apk add curl

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy all the files to the container
COPY --chown=nonroot:nonroot . .
RUN mv .env.local .env

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN export FLASK_APP=app.py
RUN pip install -r requirements.txt

# migrate database
# RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

# ENTRYPOINT ["/home/app/docker-entrypoint.sh"]
CMD ["python", "app.py"]