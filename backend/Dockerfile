FROM python:3.9-slim-buster

WORKDIR /usr/src/app

RUN pip3 install openai nltk flask

COPY . ./


CMD ["python3", "main.py"]