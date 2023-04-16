FROM python:3.9.16-slim-bullseye

WORKDIR /code

COPY ./staging /code/staging

COPY ./credentials /code/credentials

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/main.py

COPY ./bfsa /code/bfsa

COPY ./.env /code/.env

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
