ARG PYTHON_IMAGE=python:3.14-slim@sha256:cd89c30eda26ee911a4611b18680086e0ea42e6f5f8cbe653d07fa7958c9cec8
FROM ${PYTHON_IMAGE}

ARG LOCK=requirements/pygame-ce.txt
ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    SDL_VIDEODRIVER=dummy \
    SDL_AUDIODRIVER=dummy \
    PATH=/opt/venv/bin:$PATH

COPY ${LOCK} /tmp/requirements.txt
RUN python -m venv /opt/venv \
    && pip install --require-hashes --no-deps --only-binary=:all: -r /tmp/requirements.txt \
    && useradd --create-home --uid 10001 app

USER app
WORKDIR /home/app/src
COPY --chown=app:app pyproject.toml README.md accept_mouse_click.py ./
COPY --chown=app:app tests ./tests

CMD ["sh", "-c", "ruff check . && ruff format --check . && pytest -p no:cacheprovider"]
