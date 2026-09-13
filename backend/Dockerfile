# Backend image. Multi-stage so the wheels are built once and the runtime layer
# carries no compiler and no build cache.
FROM python:3.12-slim AS build

WORKDIR /wheels
COPY requirements.lock.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.lock.txt


FROM python:3.12-slim AS runtime

# Runs as a non-root user. The container has no reason to be root and Kyverno
# and Pod Security Standards will refuse it later if it is.
RUN useradd --create-home --uid 10001 app

WORKDIR /app
# WORKDIR creates /app owned by root. The app writes audit.log into its working
# directory at import time, so the directory itself has to be writable by the
# non-root user, not only the files copied into it.
RUN chown app:app /app

COPY --from=build /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
 && rm -rf /wheels

COPY --chown=app:app app ./app
COPY --chown=app:app static ./static
COPY --chown=app:app db ./db

USER app

EXPOSE 8000

# The same endpoint compose waits on. Uses urllib because this image has no
# curl and adding one for a health check is not worth the attack surface.
HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=6 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
