FROM python:3.12-slim

RUN apt update && apt install -y bash nano

WORKDIR /home

RUN pip install --no-cache-dir --upgrade pip

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt