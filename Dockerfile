FROM python:3-alpine

LABEL maintainer="Engenharia Arquivei <engenharia@arquivei.com.br>"

ARG HTTP_PORT
ENV HTTP_PORT=8000

COPY . /application
WORKDIR /application

RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "/application/main.py" ]

EXPOSE ${HTTP_PORT}