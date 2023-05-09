import settings
import os
import logging
import uuid
from DB.setup_db import get_cursor, get_cursor_fix
from multiprocessing import Pool, Lock, current_process
from fingerprint import fingerprint_file

KNOWN_EXTENSIONS = ["mp3", "wav", "flac", "m4a"]


def register_directory(path, radio_name, fix_soud_name):
    """Recursively register songs in a directory.

    Uses :data:`~abracadabra.settings.NUM_WORKERS` workers in a pool to register songs in a
    directory.

    :param path: Path of directory to register
    """
    def pool_init(l):
        """Init function that makes a lock available to each of the workers in
        the pool. Allows synchronisation of db writes since SQLite only supports
        one writer at a time.
        """
        global lock
        lock = l
        logging.info(f"Pool init in {current_process().name}")

    to_register = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.split('.')[-1] not in KNOWN_EXTENSIONS:
                continue
            file_path = os.path.join(path, root, f)
            to_register.append((file_path, radio_name, fix_soud_name))
    l = Lock()
    with Pool(settings.NUM_WORKERS, initializer=pool_init, initargs=(l,)) as p:
        p.map(register_song, to_register)
    # speed up future reads
    checkpoint_db()
    
def checkpoint_db():
    with get_cursor() as (conn, c):
        c.execute("PRAGMA wal_checkpoint(FULL)")


def song_in_db(filename):
    """Check whether a path has already been registered.

    :param filename: The path to check.
    :returns: Whether the path exists in the database yet.
    :rtype: bool
    """
    with get_cursor() as (conn, c):
        song_id = str(uuid.uuid5(uuid.NAMESPACE_OID, filename).int)
        c.execute("SELECT * FROM song_info WHERE song_id=?", (song_id,))
        return c.fetchone() is not None
        
def register_song(filename, program_name, fix_sound_name):
    """Register a single song.

    Checks if the song is already registered based on path provided and ignores
    those that are already registered.

    :param filename: Path to the file to register"""
    if song_in_db(filename):
        return
    hashes = fingerprint_file(filename)
    song_info = (program_name, fix_sound_name)
    try:
        logging.info(f"{current_process().name} waiting to write {filename}")
        with lock:
            logging.info(f"{current_process().name} writing {filename}")
            store_song(hashes, song_info)
            logging.info(f"{current_process().name} wrote {filename}")
    except NameError:
        logging.info(f"Single-threaded write of {filename}")
        # running single-threaded, no lock needed
        store_song(hashes, song_info)
        
def store_song(hashes, song_info):
    """Register a song in the database.

    :param hashes: A list of tuples of the form (hash, time offset, song_id) as returned by
        :func:`~abracadabra.fingerprint.fingerprint_file`.
    :param song_info: A tuple of form (artist, album, title) describing the song.
    """
    if len(hashes) < 1:
        # TODO: After experiments have run, change this to raise error
        # Probably should re-run the peaks finding with higher efficiency
        # or maybe widen the target zone
        return
    with get_cursor() as (conn, c):
        c.executemany("INSERT INTO hash VALUES (?, ?, ?)", hashes)
        insert_info = [i if i is not None else "Unknown" for i in song_info]
        c.execute("INSERT INTO song_info VALUES (?, ?, ?)", (*insert_info, hashes[0][2]))
        conn.commit()
        
def store_time(program_name, fix_sound_name, start_time, end_time):
    time_info = (program_name, fix_sound_name, start_time, end_time)
    with get_cursor_fix() as (conn, c):
        c.execute("INSERT INTO fix_time VALUES (?, ?, ?, ?)", (time_info))
        conn.commit()