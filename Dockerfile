FROM python:3.6-alpine

WORKDIR /app

COPY ./requirements.txt /app/
COPY ./main.py /app/

RUN pip3 install -r requirements.txt