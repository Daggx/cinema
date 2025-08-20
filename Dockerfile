FROM python:3.12-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.8.12 /uv /uvx /bin/

ADD . /app

WORKDIR /app

# Install dependencies
RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "app/manage.py", "runserver", "0.0.0.0:8000"]
