FROM python:3.9.15-alpine

RUN apk update && apk add --no-cache g++ bash nano

WORKDIR /home

RUN pip install --no-cache-dir --upgrade pip

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt