FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock README.md /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY src /app/src

CMD ["python", "-m", "src.main"]
