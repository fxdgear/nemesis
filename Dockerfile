FROM python:3.9
ARG NEMESIS_VERSION
RUN pip install --upgrade pip

RUN pip install nemesis

WORKDIR /app

ENTRYPOINT ["nemesis"]
