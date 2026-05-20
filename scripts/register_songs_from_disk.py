#!/usr/bin/env python3
"""
Register every playable folder under audio/OutputWAVS/ as a Song row.

Usage:
  python scripts/register_songs_from_disk.py           # register missing songs
  python scripts/register_songs_from_disk.py --dry-run # preview only
  python scripts/register_songs_from_disk.py --list    # show disk vs database
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(project_root / '.env')

from app import create_app, db
from app.models import Song
from app.utils.song_registry import (
    discover_playable_folders,
    parse_folder_name,
    register_songs_from_disk,
)


def list_status(output_root: Path) -> None:
    folders = discover_playable_folders(output_root)
    print(f'Playable folders on disk ({len(folders)}):\n')
    for name in folders:
        row = Song.query.filter_by(base_filename=name).first()
        if row:
            active = ' [ACTIVE]' if row.is_active else ''
            freqs = len(row.available_frequencies)
            print(f'  ✓ {name}{active}')
            print(f'      DB: {row.title} — {row.artist} ({freqs} WAV tiers)')
        else:
            print(f'  ✗ {name}  (not in database)')


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Register OutputWAVS folders as songs in the database.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be added without writing to the database',
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List disk folders and whether each exists in the database',
    )
    parser.add_argument(
        '--skip-demo',
        action='store_true',
        help='Do not register DemoSong',
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        output_root = Path(app.config['AUDIO_OUTPUT_FOLDER'])

        if args.list:
            list_status(output_root)
            return 0

        result = register_songs_from_disk(
            output_root,
            dry_run=args.dry_run,
            skip_demo=args.skip_demo,
        )

        prefix = '[dry-run] ' if args.dry_run else ''
        print(f"{prefix}Folders with WAVs: {result['total_folders']}")
        if result['added']:
            print(f"{prefix}Added ({len(result['added'])}):")
            for name in result['added']:
                if args.dry_run:
                    title, artist = parse_folder_name(name)
                    print(f'  + {name} → {title} by {artist}')
                else:
                    row = Song.query.filter_by(base_filename=name).first()
                    if row:
                        print(f'  + {name} → {row.title} by {row.artist}')
                    else:
                        print(f'  + {name}')
        if result['updated']:
            print(f"Updated ({len(result['updated'])}): {', '.join(result['updated'])}")
        if result['skipped']:
            print(f"Already in DB ({len(result['skipped'])}): {', '.join(result['skipped'])}")

        if not result['added'] and not result['updated']:
            print('Nothing new to register.')
        elif not args.dry_run:
            print('\nDone. Set a song active in the admin panel or with FORCE_PLAYBACK_BASE_FILENAME in .env.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
