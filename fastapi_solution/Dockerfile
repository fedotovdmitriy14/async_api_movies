FROM python:3.9.0-slim-buster

WORKDIR app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -U setuptools pip \
     && pip install -r requirements.txt

EXPOSE 8000

COPY . .

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
