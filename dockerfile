FROM python:3.12

RUN mkdir /kinopoisk

WORKDIR /kinopoisk

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /kinopoisk/docker/*.sh

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind=0.0.0.0:8000"]