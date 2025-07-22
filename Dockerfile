FROM python:3.11

WORKDIR /app

COPY . /app
COPY .env /app/.env


RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
