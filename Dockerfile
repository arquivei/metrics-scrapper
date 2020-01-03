FROM python:3-alpine

ARG HTTP_PORT
ENV HTTP_PORT=8000

COPY . /application
WORKDIR /application

RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "/application/main.py" ]

EXPOSE ${HTTP_PORT}