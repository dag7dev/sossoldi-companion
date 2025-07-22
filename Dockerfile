FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install poetry

RUN poetry config virtualenvs.create false --local
RUN poetry install --no-interaction --no-ansi
RUN poetry install

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
