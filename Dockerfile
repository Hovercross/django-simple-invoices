FROM python:3.12-bookworm as builder

WORKDIR /app

RUN pip install pip==23.3.1
RUN pip install poetry==1.7.1

COPY poetry.lock pyproject.toml /app/

RUN python -m venv --copies /app/.venv
RUN . /app/.venv/bin/activate && poetry install

FROM python:3.12-slim-bookworm as prod
RUN apt-get update && apt-get install -y postgresql-client

COPY --from=builder /app/.venv /app/.venv/
ENV PATH /app/.venv/bin:$PATH

WORKDIR /app
COPY . ./

ARG DOCKER_BUILD=TRUE
RUN python manage.py collectstatic --no-input
EXPOSE 8000

CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--bind", ":8000", "core.asgi:application", "-k", "uvicorn.workers.UvicornWorker"]