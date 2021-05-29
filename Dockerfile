FROM python:3.9-slim

WORKDIR /app

RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --deploy

COPY . .

CMD [ "gunicorn",  "webapp:app", "-b", "0.0.0.0:8000"]
