FROM python:3.9.0-slim-buster

WORKDIR app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -U setuptools pip \
     && pip install -r requirements.txt

COPY . .

RUN python main.py
