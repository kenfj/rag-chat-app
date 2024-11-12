# Stage 1: Build and Test
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder

WORKDIR /var/task

ENV ENV=development

RUN pip install --no-cache-dir black flake8 isort poetry

COPY pyproject.toml poetry.lock ./
# --no-root: https://stackoverflow.com/questions/77757777
RUN poetry install --no-interaction --no-root --no-ansi && \
    # https://python-poetry.org/docs/cli/#export
    poetry export --without-hashes -f requirements.txt --output requirements.txt

COPY .flake8 ./
COPY src/ ./src/
COPY static/ ./static/
COPY [".env.development", ".env.production", "./"]

RUN flake8 src && \
    black --check --diff src && \
    isort --check-only --diff src


# Stage 2: Final Image
# https://github.com/awslabs/aws-lambda-web-adapter/tree/main/examples/fastapi
FROM public.ecr.aws/docker/library/python:3.12-slim
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /var/task

ENV PORT=8000
ENV PYTHONPATH=/var/task/src

COPY --from=builder /var/task/requirements.txt /var/task/requirements.txt
RUN python -m pip install -r requirements.txt

COPY --from=builder /var/task/src /var/task/src
COPY --from=builder /var/task/static /var/task/static
COPY [".env.development", ".env.production", "./"]

CMD ["sh", "-c", "exec uvicorn --host=0.0.0.0 --port=${PORT} main:app"]
