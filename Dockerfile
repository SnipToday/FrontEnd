FROM python:3.5

ENV DJANGO_CONFIGURATION Docker

RUN mkdir /code

COPY requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY . /code/

WORKDIR /code


