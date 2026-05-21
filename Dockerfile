# Optional: deploy to Fly.io, Railway (Docker), or any container host.
# Mount a volume at /var/data for audio WAVs and uploads.

FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    AUDIO_OUTPUT_FOLDER=/var/data/OutputWAVS \
    UPLOAD_FOLDER=/var/data/uploads \
    LOG_FILE=/var/data/logs/app.log

RUN mkdir -p /var/data/OutputWAVS /var/data/uploads /var/data/logs

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
