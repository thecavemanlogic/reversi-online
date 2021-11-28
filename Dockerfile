FROM python:3.9.7-slim-buster

RUN pip3 install Flask==2.0.2 flask-socketio==5.1.1 gunicorn==20.1.0 eventlet==0.30.2

COPY . /app
WORKDIR /app

ENTRYPOINT [ "/bin/bash", "run.sh" ]