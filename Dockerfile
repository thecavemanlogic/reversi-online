FROM python:3.9.9-alpine3.14

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/bin/ash", "run.sh" ]