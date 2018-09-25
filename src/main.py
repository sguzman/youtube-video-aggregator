import bs4
import requests
import queue
import threading
import psycopg2
import json
import random
from multiprocessing.dummy import Pool
import youtube.videos


seen = queue.Queue()
cores = 8
pool = Pool(cores)
conn = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')


def get_chans():
    postgresql_select_query = 'SELECT * FROM youtube.channels.channels'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()
    print(len(records), 'channels from table')

    cursor.close()
    return records


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


def insert_vids(cursor, channel_id, data, incumbent_videos):
    sql_insert_chann = 'INSERT INTO youtube.channels.videos (chan_id, video_id) VALUES (%s, %s)'

    print(channel_id)
    hit_one = False
    for datum in data:
        hit_one = datum not in incumbent_videos
        if hit_one:
            print(datum, end=', ')
            cursor.execute(sql_insert_chann, [channel_id, datum])

    if hit_one:
        print()


def insertion_daemon():
    vids = get_vids()

    while True:
        channel_id, videos = seen.get(block=True)
        cursor = conn.cursor()
        insert_vids(cursor, channel_id, videos, vids)
        conn.commit()
        cursor.close()


def channel_process(chan):
    chan_serial = chan[0]
    chan_id = chan[1]

    vids = youtube.videos.videos(chan_serial)
    seen.put((chan_id, vids))


def main():
    threading.Thread(target=insertion_daemon, daemon=True).start()
    channels = get_chans()
    random.shuffle(channels)

    pool.map(channel_process, channels)
    print('done')


main()
