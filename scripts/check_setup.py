#!/usr/bin/env python3
"""
Check that Phase 2 prerequisites are configured before backend/API work.

Usage:
  python scripts/check_setup.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / '.env'
ENV_EXAMPLE = PROJECT_ROOT / '.env.example'


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass


def _status(ok: bool) -> str:
    return 'OK' if ok else 'MISSING'


def main() -> int:
    _load_dotenv()
    issues: list[str] = []
    warnings: list[str] = []

    print('Frequent Listener — setup check\n')
    print(f'Project root: {PROJECT_ROOT}\n')

    # .env file
    has_env = ENV_PATH.is_file()
    print(f'[{_status(has_env)}] .env file exists')
    if not has_env:
        issues.append(
            'Create .env: cp .env.phase2.template .env  (or cp .env.example .env)'
        )

    # SECRET_KEY
    sk = (os.environ.get('SECRET_KEY') or '').strip()
    sk_ok = bool(sk) and sk not in (
        'change-me-to-a-long-random-string',
        'FILL_IN_RANDOM_SECRET_KEY',
        'dev-secret-key-change-in-production',
    )
    print(f'[{_status(sk_ok)}] SECRET_KEY set to a non-placeholder value')
    if not sk_ok:
        issues.append(
            'Set SECRET_KEY in .env — run: python -c "import secrets; print(secrets.token_hex(32))"'
        )

    # ADMIN_PASSWORD
    admin_pw = (os.environ.get('ADMIN_PASSWORD') or '').strip()
    admin_ok = bool(admin_pw) and admin_pw not in (
        'changeme-dev-only',
        'FILL_IN_YOUR_ADMIN_PASSWORD',
    )
    print(f'[{_status(admin_ok)}] ADMIN_PASSWORD set (not default placeholder)')
    if not admin_ok:
        warnings.append(
            'Set ADMIN_PASSWORD in .env, then run: python scripts/create_admin.py'
        )

    # Spotify
    cid = (os.environ.get('SPOTIFY_CLIENT_ID') or '').strip()
    csec = (os.environ.get('SPOTIFY_CLIENT_SECRET') or '').strip()
    spotify_ok = bool(cid and csec) and not cid.startswith('FILL_IN')
    print(f'[{_status(spotify_ok)}] SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET')
    if not spotify_ok:
        issues.append(
            'Add Spotify keys from https://developer.spotify.com/dashboard to .env'
        )

    # ffmpeg
    ffmpeg_path = shutil.which('ffmpeg')
    ffmpeg_ok = ffmpeg_path is not None
    print(f'[{_status(ffmpeg_ok)}] ffmpeg on PATH{f" ({ffmpeg_path})" if ffmpeg_path else ""}')
    if not ffmpeg_ok:
        warnings.append(
            'Install ffmpeg (brew install ffmpeg) — required to test admin song processing'
        )

    # Database
    db_path = PROJECT_ROOT / 'data' / 'game.db'
    db_ok = db_path.is_file()
    print(f'[{_status(db_ok)}] SQLite database at data/game.db')
    if not db_ok:
        warnings.append('Run: python scripts/init_db.py')

    # Output WAV folders
    out_root = PROJECT_ROOT / 'audio' / 'OutputWAVS'
    wav_folders = 0
    if out_root.is_dir():
        for p in out_root.iterdir():
            if p.is_dir() and any(p.glob('reconstructed_audio_*.wav')):
                wav_folders += 1
    wav_ok = wav_folders > 0
    print(f'[{_status(wav_ok)}] Song folders with frequency WAVs ({wav_folders} found)')
    if not wav_ok:
        warnings.append(
            'No reconstructed_audio_*.wav under audio/OutputWAVS/ — run init_db or process a song'
        )

    # Optional: quick Spotify API test
    if spotify_ok:
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from app import create_app

            app = create_app()
            with app.app_context():
                import spotipy
                from spotipy.oauth2 import SpotifyClientCredentials

                auth = SpotifyClientCredentials(
                    client_id=cid,
                    client_secret=csec,
                )
                sp = spotipy.Spotify(auth_manager=auth)
                sp.search('test', limit=1)
            print('[OK] Spotify API credentials accepted')
        except Exception as exc:
            print('[MISSING] Spotify API test failed')
            issues.append(f'Spotify API error: {exc}')

    print('\n--- Summary ---')
    if warnings:
        print('\nWarnings (recommended):')
        for w in warnings:
            print(f'  • {w}')
    if issues:
        print('\nBlockers (fix before Phase 2):')
        for i in issues:
            print(f'  • {i}')
        print('\nSee docs/PHASE2_SETUP.md for details.')
        return 1

    print('\nAll required checks passed. Optional warnings above may still apply.')
    print('See docs/PHASE2_SETUP.md for smoke tests, then start Phase 2 implementation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
