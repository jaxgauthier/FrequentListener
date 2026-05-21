"""Lightweight schema upgrades (no Alembic) for existing SQLite/Postgres DBs."""

from sqlalchemy import inspect, text

from app import db


def ensure_schema_upgrades() -> None:
    """Add columns introduced after first deploy; safe to run every release."""
    engine = db.engine
    inspector = inspect(engine)
    dialect = engine.dialect.name

    if inspector.has_table('songs'):
        cols = {c['name'] for c in inspector.get_columns('songs')}
        if 'is_deleted' not in cols:
            if dialect == 'postgresql':
                stmt = (
                    'ALTER TABLE songs ADD COLUMN is_deleted BOOLEAN '
                    'DEFAULT FALSE NOT NULL'
                )
            else:
                stmt = (
                    'ALTER TABLE songs ADD COLUMN is_deleted BOOLEAN '
                    'DEFAULT 0 NOT NULL'
                )
            with engine.begin() as conn:
                conn.execute(text(stmt))

    if inspector.has_table('user_stats'):
        cols = {c['name'] for c in inspector.get_columns('user_stats')}
        if 'final_score' not in cols:
            with engine.begin() as conn:
                conn.execute(
                    text('ALTER TABLE user_stats ADD COLUMN final_score INTEGER')
                )
