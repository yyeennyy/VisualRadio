import uuid
import sqlite3
from collections import defaultdict
from contextlib import contextmanager
import settings

@contextmanager
def get_cursor():
    """Get a connection/cursor to the database.

    :returns: Tuple of connection and cursor.
    """
    try:
        conn = sqlite3.connect(settings.DB_PATH, timeout=30)
        yield conn, conn.cursor()
    finally:
        conn.close()
        
@contextmanager
def get_cursor_fix():
    """Get a connection/cursor to the database.

    :returns: Tuple of connection and cursor.
    """
    try:
        conn = sqlite3.connect(settings.FIX_DB_PATH, timeout=30)
        yield conn, conn.cursor()
    finally:
        conn.close()

def setup_db():
    """Create the database and tables.

    To be run once through an interactive shell.
    """
    with get_cursor() as (conn, c):
        c.execute("CREATE TABLE IF NOT EXISTS hash (hash int, offset real, song_id text)")
        c.execute("CREATE TABLE IF NOT EXISTS song_info (program_name text, fix_sound_name text, song_id text)")
        # dramatically speed up recognition
        c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON hash (hash)")
        # faster write mode that enables greater concurrency
        # https://sqlite.org/wal.html
        c.execute("PRAGMA journal_mode=WAL")
        # reduce load at a checkpoint and reduce chance of a timeout
        c.execute("PRAGMA wal_autocheckpoint=300")
        
