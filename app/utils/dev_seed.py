"""
Development defaults: admin user password and a working default active song.
Does not replace an active song that already has WAVs on disk (even partial tiers).
When picking a default, prefers your downloaded DB songs over DemoSong.
"""

from pathlib import Path

import numpy as np
import soundfile as sf
from flask import current_app

from app import db
from app.models import Song
from app.models.user import AdminUser

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'MadJax195'
DEMO_SONG_BASE = 'DemoSong'

_PREFERRED_OUTPUT_FOLDERS = [
    'Milan',
    'GhostTown',
    'MrBrightside',
    'MrBrighstide',
    'TeenageDirtbag',
]

_FOLDER_SONG_INFO = {
    'Milan': ('Milan', 'Unknown Artist'),
    'GhostTown': ('Ghost Town', 'Unknown Artist'),
    'MrBrightside': ('Mr. Brightside', 'The Killers'),
    'MrBrighstide': ('Mr. Brightside', 'The Killers'),
    'TeenageDirtbag': ('Teenage Dirtbag', 'Wheatus'),
    'DemoSong': ('Demo Track', 'Demo Artist'),
}


def ensure_admin_user() -> None:
    admin = AdminUser.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first()
    if not admin:
        admin = AdminUser(
            username=DEFAULT_ADMIN_USERNAME,
            email='admin@example.com',
        )
        db.session.add(admin)
    admin.set_password(DEFAULT_ADMIN_PASSWORD)


def _song_has_playable_files(song: Song) -> bool:
    from app.services.audio_service import AudioService

    return len(AudioService.get_available_frequencies(song.base_filename)) > 0


def _folder_wav_count(folder: Path) -> int:
    if not folder.is_dir():
        return 0
    n = 0
    for f in folder.iterdir():
        if not f.is_file():
            continue
        if f.name.startswith('reconstructed_audio_') and f.name.endswith('.wav'):
            n += 1
    return n


def _pick_best_output_folder(out_root: Path) -> str | None:
    """Folder with the most frequency WAVs; ties favor anything other than DemoSong."""
    if not out_root.is_dir():
        return None
    scored: list[tuple[str, int]] = []
    for p in out_root.iterdir():
        if not p.is_dir():
            continue
        c = _folder_wav_count(p)
        if c > 0:
            scored.append((p.name, c))
    if not scored:
        return None
    max_c = max(t[1] for t in scored)
    best = [name for name, c in scored if c == max_c]
    non_demo = [n for n in best if n != DEMO_SONG_BASE]
    return (non_demo or best)[0]


def _pick_newest_db_song_with_files() -> Song | None:
    """Prefer latest non-demo song that has WAVs; otherwise latest demo with WAVs."""
    rows = Song.query.order_by(Song.created_at.desc()).all()
    demo: Song | None = None
    for s in rows:
        if not _song_has_playable_files(s):
            continue
        if s.base_filename == DEMO_SONG_BASE:
            if demo is None:
                demo = s
            continue
        return s
    return demo


def _set_only_active(song: Song) -> None:
    for s in Song.query.all():
        s.is_active = False
    song.is_active = True


def _write_demo_frequency_wavs(song_dir: Path, levels: list) -> None:
    """Write short mono PCM_16 WAVs (browser-friendly); always overwrites."""
    song_dir.mkdir(parents=True, exist_ok=True)
    sr = int(current_app.config['AUDIO_SAMPLE_RATE'])
    duration = min(int(current_app.config['AUDIO_DURATION']), 30)
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    mono = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float64)
    pcm = np.clip(np.round(mono * 32767.0), -32768, 32767).astype(np.int16)
    for fc in levels:
        path = song_dir / f'reconstructed_audio_{fc}.wav'
        sf.write(str(path), pcm, sr, subtype='PCM_16', format='WAV')


def ensure_default_song_works() -> None:
    """
    If the active song already has at least one frequency file on disk, leave it alone.
    Otherwise pick: newest downloaded row with files → best OutputWAVS folder → DemoSong.
    Caller should db.session.commit() after this (no commit here).
    """
    levels = list(current_app.config['FREQUENCY_LEVELS'])
    out_root = Path(current_app.config['AUDIO_OUTPUT_FOLDER'])

    active = Song.query.filter_by(is_active=True).first()
    if active and _song_has_playable_files(active):
        # If DemoSong is active but a real download exists, prefer the download.
        if active.base_filename == DEMO_SONG_BASE:
            better = _pick_newest_db_song_with_files()
            if better is not None and better.id != active.id:
                _set_only_active(better)
        return

    if active:
        active.is_active = False

    picked = _pick_newest_db_song_with_files()
    if picked:
        _set_only_active(picked)
        return

    chosen_folder = _pick_best_output_folder(out_root)
    if chosen_folder and chosen_folder != DEMO_SONG_BASE:
        song = Song.query.filter_by(base_filename=chosen_folder).first()
        if not song:
            title, artist = _FOLDER_SONG_INFO.get(
                chosen_folder,
                (chosen_folder.replace('_', ' '), 'Unknown Artist'),
            )
            song = Song(
                title=title,
                artist=artist,
                album=None,
                base_filename=chosen_folder,
                has_frequency_versions=True,
                is_active=False,
            )
            db.session.add(song)
            db.session.flush()
        _set_only_active(song)
        return

    # Only DemoSong on disk or nothing — ensure PCM demo files exist
    chosen = DEMO_SONG_BASE
    _write_demo_frequency_wavs(out_root / DEMO_SONG_BASE, levels)

    title, artist = _FOLDER_SONG_INFO[DEMO_SONG_BASE]
    song = Song.query.filter_by(base_filename=chosen).first()
    if not song:
        song = Song(
            title=title,
            artist=artist,
            album=None,
            base_filename=chosen,
            has_frequency_versions=True,
            is_active=False,
        )
        db.session.add(song)
    else:
        song.has_frequency_versions = True

    db.session.flush()
    _set_only_active(song)


def ensure_dev_defaults() -> None:
    ensure_admin_user()
    ensure_default_song_works()
    db.session.commit()
