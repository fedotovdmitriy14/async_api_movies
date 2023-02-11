FROM python:3.10-slim-buster

WORKDIR fastapi_solution/tests/functional

ENV PYTHONPATH "${PYTHONPATH}:/fastapi_solution"

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -U setuptools pip \
     && pip install -r requirements.txt

COPY . .
