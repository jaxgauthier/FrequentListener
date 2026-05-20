#!/usr/bin/env python3
"""
Test the weekly song queue without waiting until tomorrow.

Usage:
  python scripts/test_queue_activation.py --list
  python scripts/test_queue_activation.py              # activate today's queued song
  python scripts/test_queue_activation.py --date 2026-05-21
  python scripts/test_queue_activation.py --dry-run --date 2026-05-21
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(project_root / '.env')

from app import create_app
from app.models.song import Song, SongQueue
from app.services.audio_service import AudioService
from app.services.queue_service import QueueService


def list_queue(week_start: date | None = None) -> None:
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=7)
    entries = (
        SongQueue.query.filter(
            SongQueue.scheduled_date >= week_start,
            SongQueue.scheduled_date < week_end,
            SongQueue.status != 'deleted',
        )
        .order_by(SongQueue.scheduled_date)
        .all()
    )

    print(f'Queue for week starting {week_start.isoformat()} (Mon–Sun):\n')
    if not entries:
        print('  (empty — queue songs in the admin panel first)')
        return

    today = date.today()
    for entry in entries:
        song = entry.song
        wavs = len(AudioService.get_available_frequencies(song.base_filename)) if song else 0
        day_label = entry.scheduled_date.strftime('%A %Y-%m-%d')
        markers = []
        if entry.scheduled_date == today:
            markers.append('TODAY')
        if song and song.is_active:
            markers.append('ACTIVE')
        marker_str = f" [{', '.join(markers)}]" if markers else ''
        playable = 'playable' if wavs > 0 else 'NO WAV FILES'
        print(
            f"  {day_label}{marker_str}: {song.title} — {song.artist} "
            f"(status={entry.status}, {wavs} tiers, {playable})"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description='Test queue activation by date')
    parser.add_argument(
        '--list',
        action='store_true',
        help='Show this week’s queue and whether each song has WAV files',
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Activate queued song for this date (YYYY-MM-DD), e.g. tomorrow',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='With --date: only show what would activate, do not change DB',
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.list:
            list_queue()
            return 0

        target = date.fromisoformat(args.date) if args.date else date.today()
        entry = SongQueue.query.filter_by(
            scheduled_date=target,
            status='queued',
        ).first()

        if not entry:
            print(f'No queued song for {target.isoformat()} ({target.strftime("%A")}).')
            print('Queue songs in admin, or run: python scripts/test_queue_activation.py --list')
            return 1

        song = entry.song
        wavs = len(AudioService.get_available_frequencies(song.base_filename))
        print(f'Queued for {target.isoformat()}: {song.title} by {song.artist}')
        print(f'  WAV tiers on disk: {wavs}')
        if wavs == 0:
            print('  WARNING: no playable files — game will not work for this song.')

        if args.dry_run:
            print('  [dry-run] Would activate this song and reset play state.')
            return 0

        activated = QueueService.activate_song_for_date(target)
        if activated:
            print(f'  Activated: {activated.title} by {activated.artist}')
            print(f'  Open http://127.0.0.1:{app.config.get("PORT", 5001)}/ to play it.')
        return 0

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
