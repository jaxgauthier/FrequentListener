# Deploying Frequent Listener

This app is a **Flask + Postgres + on-disk WAV files** service. Use a platform with a **persistent disk** (or plan for S3 later). **Vercel is not recommended** for this repo.

Recommended hosts: **Railway**, **Render**, **Fly.io**, or a **VPS**.

---

## What was added for deploy

| File | Purpose |
|------|---------|
| `wsgi.py` | Gunicorn entrypoint + HTTPS proxy fix |
| `gunicorn.conf.py` | Workers, timeout (120s for admin processing) |
| `Procfile` | Railway / Heroku-style `web` + `release` |
| `render.yaml` | Render blueprint (web + Postgres) |
| `nixpacks.toml` | Railway: install `ffmpeg` |
| `Dockerfile` | Optional container deploy |
| `scripts/release.py` | Migrations + admin user on each deploy |

---

## Required environment variables (production)

| Variable | Notes |
|----------|--------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Random 32+ chars |
| `DATABASE_URL` | Postgres (`postgres://` is auto-fixed to `postgresql://`) |
| `ADMIN_PASSWORD` | Then run release or `create_admin` once |
| `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` | Admin search |
| `PORT` | Set by host (Render/Railway inject this) |

**Optional (persistent disk paths):**

| Variable | Example |
|----------|---------|
| `AUDIO_OUTPUT_FOLDER` | `/var/data/OutputWAVS` |
| `UPLOAD_FOLDER` | `/var/data/uploads` |
| `LOG_FILE` | `/var/data/logs/app.log` |

Do **not** set `FORCE_PLAYBACK_BASE_FILENAME` in production unless debugging.

---

## Option A — Render (blueprint in repo)

1. Push repo to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** → connect repo (`render.yaml`).
3. Set sync=false secrets in the UI: `ADMIN_PASSWORD`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`.
4. **Attach a persistent disk** to the web service:
   - Mount path: `/var/data`
   - Size: 1GB+ (WAVs add up)
5. Redeploy. `releaseCommand` runs `scripts/release.py` automatically.
6. Copy existing WAVs to the disk (SFTP/shell) or process songs via admin after deploy.
7. Register songs:  
   `python scripts/register_songs_from_disk.py` (one-off shell on Render).

**Cron (daily song):** Render Cron Job → command:

```bash
python scripts/daily_activation.py
```

Same env vars as the web service.

---

## Option B — Railway

1. New project → **Deploy from GitHub** → this repo.
2. Add **PostgreSQL** plugin → copy `DATABASE_URL` into service variables.
3. Variables: `FLASK_ENV=production`, `SECRET_KEY`, `ADMIN_PASSWORD`, Spotify keys.
4. Add a **volume** mounted at `/var/data` and set:
   - `AUDIO_OUTPUT_FOLDER=/var/data/OutputWAVS`
   - `UPLOAD_FOLDER=/var/data/uploads`
5. Railway reads `Procfile` (`web` + `release`). `nixpacks.toml` installs ffmpeg.
6. Cron: Railway scheduled task → `python scripts/daily_activation.py`.

---

## Option C — Fly.io (Docker)

```bash
fly launch   # use Dockerfile in repo
fly volumes create frequent_data --size 1
# Mount volume at /var/data in fly.toml
fly secrets set SECRET_KEY=... DATABASE_URL=... ADMIN_PASSWORD=... \
  SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET=... \
  FLASK_ENV=production
fly deploy
fly ssh console -C "python scripts/release.py"
```

---

## Option D — VPS (most control)

1. Ubuntu 22.04+, Python 3.11, ffmpeg, nginx, certbot.
2. Clone repo, venv, `pip install -r requirements.txt`.
3. Postgres locally or managed (Neon, Supabase).
4. systemd unit for gunicorn:

```ini
[Service]
WorkingDirectory=/opt/FrequentListener
Environment=FLASK_ENV=production
EnvironmentFile=/opt/FrequentListener/.env
ExecStart=/opt/FrequentListener/.venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
```

5. nginx reverse proxy → `proxy_set_header X-Forwarded-Proto https;`
6. cron: `0 0 * * * cd /opt/FrequentListener && .venv/bin/python scripts/daily_activation.py`

---

## After first deploy

```bash
# On the server (or local against prod DATABASE_URL):
FLASK_ENV=production python scripts/release.py
FLASK_ENV=production ADMIN_PASSWORD=yourpass python scripts/create_admin.py
FLASK_ENV=production python scripts/register_songs_from_disk.py
```

Smoke test:

- `https://your-domain/health` → `{"status":"healthy",...}`
- Play audio, submit guess, admin login, Spotify search

---

## Local production dry-run

```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export DATABASE_URL=postgresql://user:pass@localhost:5432/frequent_listener
export ADMIN_PASSWORD=local-prod-test
python scripts/release.py
gunicorn -c gunicorn.conf.py wsgi:app
```

---

## YouTube “Sign in to confirm you're not a bot” on Render

Render uses **datacenter IPs**. YouTube often blocks admin **Process song** downloads there even when it works on your Mac.

**Recommended (most reliable):** process songs **locally**, then put WAVs on the server:

```bash
# On your Mac (with .env + ffmpeg)
python run.py
# Admin → process song, or use existing audio/OutputWAVS folders

# Register DB rows locally, or on Render Shell after copying files:
python scripts/register_songs_from_disk.py
```

Copy folders to the Render disk (`/var/data/OutputWAVS/`) via Shell, SFTP, or rsync.

**Optional — cookies on Render:**

1. Export YouTube cookies (Netscape format) from your browser — see [yt-dlp wiki](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies).
2. Render → Web Service → **Secret Files** → add `cookies.txt`.
3. Environment: `YTDLP_COOKIES=/etc/secrets/cookies.txt`
4. Redeploy and retry Process song.

Cookies expire; you may need to re-export. This still may fail on some hosts.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| App crashes on boot | Missing `SECRET_KEY` or `DATABASE_URL` in production |
| No audio | WAVs not on persistent disk; wrong `AUDIO_OUTPUT_FOLDER` |
| Admin process fails | Install ffmpeg; check logs; increase `GUNICORN_TIMEOUT` |
| YouTube bot error on Render | Process locally + upload WAVs; or `YTDLP_COOKIES` secret file |
| Login loops / http cookies | Ensure HTTPS proxy headers (Render/Railway do); `SESSION_COOKIE_SECURE` |
| `psycopg2` errors | `psycopg2-binary` in requirements (already added) |

---

## Not on Vercel

Serverless limits (disk, timeouts, ffmpeg) conflict with this architecture. Use Render/Railway/Fly/VPS instead.
