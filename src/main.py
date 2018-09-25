import bs4
import requests
import queue
import threading
import psycopg2
import json
from multiprocessing.dummy import Pool


seen = queue.Queue()
cores = 8
pool = Pool(cores)
conn = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')


def get_chans():
    postgresql_select_query = 'SELECT channel_id FROM youtube.channels.channels'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    channels = list()
    for i in records:
        channels.append(i[0])

    print(len(channels), 'channels from table')

    cursor.close()
    return channels


def get_vids():
    postgresql_select_query = 'SELECT video_id FROM youtube.channels.videos'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    channels = set()
    for i in records:
        channels.add(i[0])

    print(len(channels), 'videos from table')

    cursor.close()
    return channels


def insert_vids(cursor, data, incumbent_videos):
    sql_insert_chann = 'INSERT INTO youtube.channels.channels (channel_id) VALUES (%s)'

    for datum in data:
        if datum not in incumbent_videos:
            print(datum)
            cursor.execute(sql_insert_chann, [datum])


def insertion_daemon():
    vids = get_vids()

    while True:
        channel_id, videos = seen.get(block=True)
        cursor = conn.cursor()
        insert_vids(cursor, channel_id, vids)
        conn.commit()
        cursor.close()


def main():
    threading.Thread(target=insertion_daemon, daemon=True).start()
    channels = get_chans(conn)

    pool.map(vids, channels)
    print('done')
