# Frequent Listener

A Flask game where users guess songs from FFT-reconstructed audio clips. Reveal more frequency bands to hear more of the song — but your score goes down. An admin panel queues songs (Spotify metadata + YouTube audio), runs the Fourier pipeline, and manages the weekly queue.

## How it works

- **User side:** Play the active song, reveal tiers (500 Hz → 7500 Hz), submit a guess, view stats and history when logged in.
- **Admin side:** Search Spotify, download a clip from YouTube, generate frequency WAVs, queue up to 7 days, activate today’s song.
- **Data:** SQLite locally (`data/game.db`); Postgres via `DATABASE_URL` in production.

Frequency tiers (8 levels): `500, 1000, 1500, 2000, 2500, 3500, 5000, 7500` Hz. Max score per round is **8** minus how many tiers you revealed before guessing.

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python 3.11** | See `.python-version` |
| **ffmpeg** | Required for pydub / YouTube clip processing. Install before using admin “process song”. |
| **Spotify API app** | Optional for local playback of existing WAVs; **required** for admin Spotify search |

### Install ffmpeg

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y ffmpeg
```

**Windows:** Install from [ffmpeg.org](https://ffmpeg.org/download.html) and add `ffmpeg` to your `PATH`.

Verify:
```bash
ffmpeg -version
```

---

## Local setup

### 1. Clone and enter the project

```bash
cd FrequentListener
```

### 2. Create a virtual environment and install dependencies

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Or for Phase 2 prep (labeled placeholders + checklist):
cp .env.phase2.template .env
```

**Phase 2 prep:** see [docs/PHASE2_SETUP.md](docs/PHASE2_SETUP.md) and run `python scripts/check_setup.py` after filling in `.env`.

Edit `.env` at minimum:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask sessions (any long random string for dev) |
| `ADMIN_PASSWORD` | Password for the dev `admin` user created by `init_db` |
| `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` | Admin song search ([Spotify Dashboard](https://developer.spotify.com/dashboard)) |

Optional:

| Variable | Purpose |
|----------|---------|
| `PORT` | Dev server port (default `5001`) |
| `HOST` | Bind address (default `::` — use `127.0.0.1` if `::` fails) |
| `FORCE_PLAYBACK_BASE_FILENAME` | Force game to one folder under `audio/OutputWAVS/` (e.g. `Lit_MyOwnWorstEnemy`) |

### 4. Initialize the database

```bash
python scripts/init_db.py
```

This creates:

- `data/game.db` (SQLite tables)
- `audio/uploads/`, `audio/OutputWAVS/`
- Dev `admin` user (if missing)
- Active song selection: keeps an existing playable active song, or picks the best folder with WAV files, or generates **DemoSong** sine WAVs

### 5. Run the app

```bash
python run.py
```

Open:

- **Game:** http://127.0.0.1:5001/
- **Admin:** http://127.0.0.1:5001/admin/login (`admin` + your `ADMIN_PASSWORD`)

Keep the terminal open while testing.

---

## Existing songs and test data

Processed songs live under `audio/OutputWAVS/<base_filename>/` as `reconstructed_audio_<freq>.wav`. The database `songs` table stores `base_filename`, `is_active`, and metadata.

If you already have `data/game.db` and folders (e.g. `Lit_MyOwnWorstEnemy`, `DemoSong`), **do not** rely on a hardcoded dev song — the app uses whichever row has `is_active=True` and playable files. On startup in development, `ensure_default_song_works()` only fixes the active song if nothing is playable.

To force one song for debugging, set in `.env`:

```env
FORCE_PLAYBACK_BASE_FILENAME=Lit_MyOwnWorstEnemy
```

---

## Admin: adding a new song

1. Log in at `/admin/login`.
2. Search Spotify, pick a track, set start/end time (default clip length is 10 seconds in config).
3. **Process song** — downloads via yt-dlp, converts with pydub (needs **ffmpeg**), runs FFT, writes WAVs under `audio/OutputWAVS/`.
4. Queue or set active from the admin panel.

If Spotify search fails, check `.env` credentials and restart the server after changing `.env`.

---

## Useful scripts

| Script | Purpose |
|--------|---------|
| `python scripts/init_db.py` | Create tables + dev defaults |
| `python scripts/register_songs_from_disk.py` | Add all `audio/OutputWAVS/*` folders to the database |
| `python scripts/register_songs_from_disk.py --list` | Show which folders are on disk vs in DB |
| `python scripts/create_admin.py` | Create or reset admin user |
| `python scripts/daily_activation.py` | Cron: activate today’s queued song, cleanup expired queue (production) |
| `python scripts/test_queue_activation.py --list` | See which song is scheduled each day this week |
| `python scripts/test_queue_activation.py --date YYYY-MM-DD` | Simulate activation for a future day (e.g. tomorrow) |

Player UI is based on `Fouriele game interface design/` (circular player, wave background, Fouriele branding).
| `python scripts/build_assets.py` | Build minified static bundles (optional) |

---

## Production (later)

Not required for local testing. When you deploy:

- Set `FLASK_ENV=production`
- Set `DATABASE_URL` (Postgres; Railway/Heroku often use `postgres://` — the app normalizes to `postgresql://`)
- Set a strong `SECRET_KEY`
- Run with **gunicorn** (or similar), not `python run.py` with debug
- Schedule `python scripts/daily_activation.py` daily
- Do not use default `ADMIN_PASSWORD` or commit `.env`

---

## Project layout

```
FrequentListener/
├── app/
│   ├── routes/main.py      # All HTTP routes
│   ├── models/             # User, Song, stats, queue
│   ├── services/           # Audio, Spotify, stats, queue
│   ├── templates/          # HTML pages
│   └── static/             # CSS / JS
├── audio/OutputWAVS/       # Generated frequency WAVs per song
├── data/game.db            # SQLite (gitignored)
├── scripts/                # init_db, cron, admin helpers
├── run.py                  # Dev entrypoint
├── requirements.txt
└── .env.example
```

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| No audio on play | `audio/OutputWAVS/<base_filename>/reconstructed_audio_*.wav` exist; active song in DB |
| Admin search empty | `SPOTIFY_CLIENT_ID` / `SECRET` in `.env`, restart server |
| Process song fails | `ffmpeg` on PATH; upgrade `yt-dlp` if YouTube errors |
| Wrong song plays | `is_active` in admin panel; or `FORCE_PLAYBACK_BASE_FILENAME` in `.env` |
| Port in use | Set `PORT=5002` in `.env` |
