FROM python:3.7

RUN apt-get update && apt-get -y install libatlas-base-dev libblas-dev gfortran python3-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn", "webapp:app", "-b", "0.0.0.0:8000" ]