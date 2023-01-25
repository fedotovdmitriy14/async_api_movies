FROM python:3.9.0-slim-buster

WORKDIR app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -U setuptools pip \
     && pip install -r requirements.txt

EXPOSE 8000

COPY . .

ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:8000", "-w", "4", "-k", "uvicorn.workers.UvicornH11Worker", "main:app"]
