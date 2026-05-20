# Phase 2 setup — what you need to fill in

Phase 2 fixes **APIs and backend logic** (stats, replay rules, admin auth, YouTube download).  
Most of that is code we will change. **You** only need to provide credentials and confirm your local environment.

Use this doc as a checklist. When everything is checked, tell the agent to start Phase 2 implementation.

---

## 1. Create your `.env` file

From the project root:

```bash
cp .env.example .env
```

Or copy the Phase 2 block from `.env.phase2.template` (same values, more comments).

Then fill in the sections below.

---

## 2. Required values (fill these in `.env`)

| Variable | You fill in | Used for |
|----------|-------------|----------|
| `SECRET_KEY` | A long random string (32+ chars). Example: run `python -c "import secrets; print(secrets.token_hex(32))"` | Flask sessions (login, admin) |
| `ADMIN_PASSWORD` | Password you want for admin user `admin` | `/admin/login` after `init_db` or `create_admin` |
| `SPOTIFY_CLIENT_ID` | From Spotify Developer Dashboard | Admin song search + user guess autocomplete |
| `SPOTIFY_CLIENT_SECRET` | From Spotify Developer Dashboard | Same |

**After changing `ADMIN_PASSWORD`**, reset the admin user:

```bash
python scripts/create_admin.py
```

Restart the server after any `.env` change.

---

## 3. Spotify Developer Dashboard (step-by-step)

1. Go to [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) and log in.
2. **Create app** → name e.g. `FrequentListener Dev`.
3. Open the app → **Settings**.
4. Copy **Client ID** → paste into `.env` as `SPOTIFY_CLIENT_ID=...`
5. Click **View client secret** → paste into `.env` as `SPOTIFY_CLIENT_SECRET=...`
6. You do **not** need redirect URIs for this app (client-credentials search only).
7. Save `.env`.

**Verify:** start the app, open `/admin`, search for a song (e.g. `Blink-182`). Suggestions should appear. If you see “Spotify credentials missing”, keys are wrong or the server wasn’t restarted.

---

## 4. Optional values (only if you need them)

| Variable | When to set |
|----------|-------------|
| `FORCE_PLAYBACK_BASE_FILENAME` | Force the game to one folder, e.g. `Lit_MyOwnWorstEnemy` |
| `PORT` | If `5001` is already in use 
| `HOST` | Use `127.0.0.1` if `::` causes bind errors on your Mac |
| `DATABASE_URL` | Not needed for Phase 2 local work (SQLite is default) |

---

## 5. System prerequisites (not in `.env`)

| Requirement | How to verify |
|-------------|----------------|
| **Python 3.11** + venv | `source .venv/bin/activate` |
| **ffmpeg** | `ffmpeg -version` (required before testing admin “Process song”) |
| **Local DB** | `python scripts/init_db.py` once |
| **Test songs on disk** | Folders under `audio/OutputWAVS/` with `reconstructed_audio_*.wav` |

YouTube does **not** use an API key in this project; admin download uses **yt-dlp** + ffmpeg.

---

## 6. Test accounts & data (your choices)

Fill in mentally (or on paper) what you will use while testing Phase 2:

| Item | Your value |
|------|------------|
| Admin username | `admin` (fixed) |
| Admin password | Same as `ADMIN_PASSWORD` in `.env` |
| Test user account | Create via `/signup` or use an existing username: ______________ |
| Song to test playback | Active song in DB (e.g. `Lit_MyOwnWorstEnemy`): ______________ |
| Song to test admin **process** (new download) | Pick a short, well-known track for YouTube search: ______________ |

**Note:** Processing a new song needs Spotify keys + ffmpeg and can take 1–3 minutes.

---

## 7. Verify before Phase 2 code changes

Run:

```bash
source .venv/bin/activate
python scripts/check_setup.py
```

Fix anything reported as missing, then:

```bash
python run.py
```

Manual smoke test:

- [ ] http://127.0.0.1:5001/ — audio plays for active song  
- [ ] Submit a guess (logged in or guest)  
- [ ] http://127.0.0.1:5001/admin/login — admin works  
- [ ] Admin Spotify search returns results  
- [ ] (Optional) Process one short song end-to-end  

---

## 8. What Phase 2 will fix in code (nothing for you to fill in)

These do **not** require new secrets — we implement them in the repo:

| Area | Planned fix |
|------|-------------|
| Admin APIs | Require admin login on mutate routes |
| Stats | Stop double-counting `SongStats` on guess |
| Replay | Return real `already_played` for logged-in users |
| New daily song | Reset `has_played` when active song changes |
| Song delete | Cascade related stats / player state |
| Guests | Decide policy for guest guesses vs global stats |
| YouTube | Fix yt-dlp download URL; bump package version |
| Spotify | Consolidate search through one service module |

---

## 9. Quick reference — minimal `.env` for Phase 2

```env
SECRET_KEY=paste-generated-random-string-here
ADMIN_PASSWORD=your-secure-admin-password
SPOTIFY_CLIENT_ID=paste-from-spotify-dashboard
SPOTIFY_CLIENT_SECRET=paste-from-spotify-dashboard
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5001
```

---

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| Spotify search empty / error JSON | Set both Spotify vars; restart `python run.py` |
| Admin login fails | Run `python scripts/create_admin.py` after setting `ADMIN_PASSWORD` |
| Process song fails immediately | Install ffmpeg; check terminal traceback |
| Process song fails on YouTube | Known Phase 2 fix (yt-dlp URL) — note the error message for the agent |
| No audio on home page | Set active song in admin or `FORCE_PLAYBACK_BASE_FILENAME` |

When `check_setup.py` passes and the smoke tests work, you are ready for Phase 2 implementation.

---

## Phase 2 implemented (code)

- Admin routes require login (`admin_required`)
- `/admin/logout` route added
- Guess stats: no double-count; real `already_played`; guests do not update global stats
- Active song change resets play state for that song only
- Song delete cascades stats / queue / player state
- Spotify search uses `SpotifyService`
- YouTube download uses single-step `ytsearch1` download; yt-dlp version bumped
