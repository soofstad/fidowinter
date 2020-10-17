FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

CMD python fidowinter.py

