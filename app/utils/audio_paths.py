"""
Resolve audio/OutputWAVS folder names for a song base_filename.

Handles legacy DB/folder names that do not match on-disk directories.
"""

from __future__ import annotations

import os
from pathlib import Path

# Legacy base_filename -> actual folder name under audio/OutputWAVS/
LEGACY_FOLDER_ALIASES: dict[str, str] = {
    'MrBrightside': 'TheKillers_MrBrightside',
    'MrBrighstide': 'TheKillers_MrBrightside',
    'Milan': 'Milan',
    'GhostTown': 'GhostTown',
    'TeenageDirtbag': 'TeenageDirtbag',
}


def resolve_output_folder(base_filename: str, output_root: str | Path) -> Path | None:
    """
    Return the directory containing frequency WAVs for this song, or None.
    Tries base_filename first, then legacy aliases.
    """
    if not base_filename:
        return None

    root = Path(output_root)
    direct = root / base_filename
    if direct.is_dir():
        return direct

    alias = LEGACY_FOLDER_ALIASES.get(base_filename)
    if alias:
        aliased = root / alias
        if aliased.is_dir():
            return aliased

    return None
