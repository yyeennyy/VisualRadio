import os
import logging
from multiprocessing import Pool, Lock, current_process
import numpy as np
import split.settings as settings
from split.fingerprint import fingerprint_file
import uuid
import sqlite3
from collections import defaultdict
from contextlib import contextmanager

KNOWN_EXTENSIONS = ["mp3", "wav", "flac", "m4a"]

def find_matching_offset(audio_file, threshold=5):

    # 음성 파일에서 hash 값 생성
    hashes = fingerprint_file(audio_file)
    
    # DB에서 일치하는 hash 값을 찾아 매칭 결과 가져오기
    matches = get_matches(hashes, threshold)

    # 가장 매칭 결과가 높은 음악 파일 ID 가져오기
    matched_song_id, matched_offsets = best_match_test(matches)

    # 매칭 결과가 가장 높은 음악 파일의 정보 가져오기
    matched_song_info = get_info_for_song_id(matched_song_id)

    return matched_song_info, matched_offsets

def get_matches(hashes, threshold=5):
    """Get matching songs for a set of hashes.

    :param hashes: A list of hashes as returned by
        :func:`~abracadabra.fingerprint.fingerprint_file`.
    :param threshold: Return songs that have more than ``threshold`` matches.
    :returns: A dictionary mapping ``song_id`` to a list of time offset tuples. The tuples are of
        the form (result offset, original hash offset).
    :rtype: dict(str: list(tuple(float, float)))
    """
    h_dict = {}
    for h, t, _ in hashes:
        h_dict[h] = t
    in_values = f"({','.join([str(h[0]) for h in hashes])})"
    with get_cursor() as (conn, c):
        c.execute(f"SELECT hash, offset, song_id FROM hash WHERE hash IN {in_values}")
        results = c.fetchall()
    result_dict = defaultdict(list)
    for r in results:
        result_dict[r[2]].append((r[1], h_dict[r[0]]))
    return result_dict

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
        
def best_match_test(matches):
    matched_song = None
    best_score = 0
    for song_id, offsets in matches.items():
        if len(offsets) < best_score:
            # can't be best score, avoid expensive histogram
            continue
        score = score_match(offsets)
        if score > best_score:
            best_score = score
            matched_song = song_id
            matched_offsets = offsets
    return matched_song, matched_offsets

def score_match(offsets):
    """Score a matched song.

    Calculates a histogram of the deltas between the time offsets of the hashes from the
    recorded sample and the time offsets of the hashes matched in the database for a song.
    The function then returns the size of the largest bin in this histogram as a score.

    :param offsets: List of offset pairs for matching hashes
    :returns: The highest peak in a histogram of time deltas
    :rtype: int
    """
    # Use bins spaced 0.5 seconds apart
    binwidth = 0.5
    tks = list(map(lambda x: x[0] - x[1], offsets))
    hist, _ = np.histogram(tks,
                           bins=np.arange(int(min(tks)),
                                          int(max(tks)) + binwidth + 1,
                                          binwidth))
    return np.max(hist)

def get_info_for_song_id(song_id):
    """Lookup song information for a given ID."""
    with get_cursor() as (conn, c):
        c.execute("SELECT program_name, fix_sound_name FROM song_info WHERE song_id = ?", (song_id,))
        return c.fetchone()
    
def find_time(path):
    song_info, offsets = find_matching_offset(path)
    print(offsets[-1])
    time = abs(offsets[-1][1] - offsets[-1][0])
    return song_info, time