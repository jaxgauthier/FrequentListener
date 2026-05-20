"""
Register songs from audio/OutputWAVS folders into the database.
"""

from __future__ import annotations

import re
from pathlib import Path

from app import db
from app.models import Song
from app.services.audio_service import AudioService

# folder_name -> (title, artist)
KNOWN_SONGS: dict[str, tuple[str, str]] = {
    'DemoSong': ('Demo Track', 'Demo Artist'),
    'Lit_MyOwnWorstEnemy': ('My Own Worst Enemy', 'Lit'),
    'TheKillers_MrBrightside': ('Mr. Brightside', 'The Killers'),
    'MrBrightside': ('Mr. Brightside', 'The Killers'),
    'MrBrighstide': ('Mr. Brightside', 'The Killers'),
    'FallOutBoy_SugarWereGoinDown': ("Sugar, We're Goin Down", 'Fall Out Boy'),
    'blink-182_AllTheSmallThings': ('All the Small Things', 'blink-182'),
    'blink-182_IMissYou': ("I Miss You", 'blink-182'),
    'ACDC_Thunderstruck': ('Thunderstruck', 'AC/DC'),
    'Lustra_ScottyDoesntKnow': ("Scotty Doesn't Know", 'Lustra'),
    'MötleyCrüe_KickstartMyHeart': ('Kickstart My Heart', 'Mötley Crüe'),
    'MotleyCrue_KickstartMyHeart': ('Kickstart My Heart', 'Mötley Crüe'),
    'Queen_BohemianRhapsody-Remastered2011': (
        'Bohemian Rhapsody (Remastered 2011)',
        'Queen',
    ),
    'Milan': ('Milan', 'Unknown Artist'),
    'GhostTown': ('Ghost Town', 'Unknown Artist'),
    'TeenageDirtbag': ('Teenage Dirtbag', 'Wheatus'),
}


def _humanize_title(raw: str) -> str:
    """Turn BohemianRhapsody-Remastered2011 into readable title."""
    s = raw.replace('-', ' ')
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
    s = re.sub(r'(\d+)', r' \1 ', s)
    s = ' '.join(s.split())
    return s.title() if s else raw


def parse_folder_name(folder: str) -> tuple[str, str]:
    """Return (title, artist) for a base_filename / folder name."""
    if folder in KNOWN_SONGS:
        return KNOWN_SONGS[folder]

    if '_' in folder:
        artist_part, title_part = folder.split('_', 1)
        return _humanize_title(title_part), artist_part.replace('-', ' ')

    return _humanize_title(folder), 'Unknown Artist'


def folder_has_frequency_wavs(folder: Path) -> bool:
    if not folder.is_dir():
        return False
    return any(
        p.name.startswith('reconstructed_audio_') and p.suffix == '.wav'
        for p in folder.iterdir()
        if p.is_file()
    )


def discover_playable_folders(output_root: Path) -> list[str]:
    """Folder names under output_root that contain at least one frequency WAV."""
    if not output_root.is_dir():
        return []

    names: list[str] = []
    for path in sorted(output_root.iterdir()):
        if path.is_dir() and folder_has_frequency_wavs(path):
            names.append(path.name)
    return names


def register_songs_from_disk(
    output_root: Path,
    *,
    dry_run: bool = False,
    skip_demo: bool = False,
) -> dict:
    """
    Insert Song rows for on-disk folders not already in the database.

    Returns summary dict with added/skipped/updated counts.
    """
    added: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []

    for folder_name in discover_playable_folders(output_root):
        if skip_demo and folder_name == 'DemoSong':
            skipped.append(folder_name)
            continue

        existing = Song.query.filter_by(base_filename=folder_name).first()
        title, artist = parse_folder_name(folder_name)
        wav_count = len(
            AudioService.get_available_frequencies(folder_name)
        )

        if existing:
            changed = False
            if not existing.has_frequency_versions and wav_count > 0:
                existing.has_frequency_versions = True
                changed = True
            if existing.title == existing.base_filename or existing.title == folder_name:
                existing.title = title
                existing.artist = artist
                changed = True
            if changed:
                updated.append(folder_name)
            else:
                skipped.append(folder_name)
            continue

        song = Song(
            title=title,
            artist=artist,
            album=None,
            week=1,
            base_filename=folder_name,
            has_frequency_versions=wav_count > 0,
            is_active=False,
        )
        if not dry_run:
            db.session.add(song)
        added.append(folder_name)

    if not dry_run:
        db.session.commit()

    return {
        'added': added,
        'skipped': skipped,
        'updated': updated,
        'total_folders': len(discover_playable_folders(output_root)),
    }
