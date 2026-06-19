# Multi-stage build for minimal image size
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN addgroup --system --gid 1001 redrobe && \
    adduser --system --uid 1001 --gid 1001 redrobe
COPY --from=builder /root/.local /home/redrobe/.local
COPY --chown=redrobe:redrobe . .
USER redrobe
ENV PATH=/home/redrobe/.local/bin:$PATH
ENV PYTHONPATH=/app
ENTRYPOINT ["python", "run_pipeline.py"]
