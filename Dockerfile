FROM python:3.12-bookworm as builder

WORKDIR /app

RUN pip install -U pip
RUN pip install pdm

COPY pyproject.toml pdm.lock /app/

RUN python -m venv --copies /app/.venv
RUN pdm install

FROM python:3.12-slim-bookworm as prod
RUN apt-get update && apt-get install -y postgresql-client libjpeg-dev libopenjp2-7

COPY --from=builder /app/.venv /app/.venv/
ENV PATH /app/.venv/bin:$PATH

WORKDIR /app
COPY . ./

ARG DOCKER_BUILD=TRUE
RUN python manage.py collectstatic --no-input
EXPOSE 8000

CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--bind", ":8000", "core.wsgi:application"]