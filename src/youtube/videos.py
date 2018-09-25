import bs4
import requests
import json


def json_pretty(js):
    print(json.dumps(js, indent=' ', separators={', ', ': '}))


def process_script(script):
    raw_split = script.text.split('\n')
    raw_json = raw_split[1].lstrip('    window["ytInitialData"] = ').rstrip(';')
    return json.loads(raw_json)


def select_script_tag(soup):
    for script in soup.findAll('script'):
        if script.text.startswith('\n    window["ytInitialData"]'):
            return script


def souped(url, params, headers):
    if headers is None:
        headers = {}

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/69.0.3497.100 Safari/537.36 '
    headers['User-Agent'] = user_agent

    req = requests.get(url, params=params, headers=headers)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')

    return soup


def soup_channel(chan_serial):
    url = f'https://www.youtube.com/channel/{chan_serial}/videos'
    return souped(url, None, None)


def index_nest(obj, keys):
    if len(keys) is 0:
        return obj
    else:
        return index_nest(obj[keys[0]], keys[1:])


def get_video_items_cont(obj):
    items_index = [1,
                   'response',
                   'continuationContents',
                   'gridContinuation',
                   'items'
                   ]

    json_data = index_nest(obj, items_index)
    return video_ids(json_data)


def get_cont_token_cont(obj):
    items_index = [1,
                   'response',
                   'continuationContents',
                   'gridContinuation',
                   'continuations',
                   0,
                   'nextContinuationData',
                   'continuation'
                   ]

    return index_nest(obj, items_index)


def get_video_items(obj):
    items_index = ['contents',
                   'twoColumnBrowseResultsRenderer',
                   'tabs',
                   1,
                   'tabRenderer',
                   'content',
                   'sectionListRenderer',
                   'contents',
                   0,
                   'itemSectionRenderer',
                   'contents',
                   0,
                   'gridRenderer',
                   'items'
                   ]

    json_data = index_nest(obj, items_index)
    return video_ids(json_data)


def get_cont_token(obj):
    items_index = ['contents',
                   'twoColumnBrowseResultsRenderer',
                   'tabs',
                   1,
                   'tabRenderer',
                   'content',
                   'sectionListRenderer',
                   'contents',
                   0,
                   'itemSectionRenderer',
                   'contents',
                   0,
                   'gridRenderer',
                   'continuations',
                   0,
                   'nextContinuationData',
                   'continuation',
                   ]

    return index_nest(obj, items_index)


def soup_next_page(token):
    url = f'https://www.youtube.com/browse_ajax'
    params = {
        'ctoken': token,
        'continuation': token
    }

    headers = {
        'x-spf-previous': 'https://www.youtube.com/channel/UC0rZoXAD5lxgBHMsjrGwWWQ/videos',
        'x-spf-referer': 'https://www.youtube.com/channel/UC0rZoXAD5lxgBHMsjrGwWWQ/videos',
        'x-youtube-client-name': '1',
        'x-youtube-client-version': '2.20180921',
        'x-youtube-page-cl': '214220627',
        'x-youtube-page-label': 'youtube.ytfe.desktop_20180921_0_RC2',
        'x-youtube-utc-offset': '-420',
        'x-youtube-variants-checksum': '00589810531d478dd01596fd6f1241e0'
    }
    return souped(url, params, headers)


def video_ids(items):
    vids = []
    for item in items:
        grid = item['gridVideoRenderer']['videoId']
        vids.append(grid)

    return vids


def main():
    chan_serial = 'UC0rZoXAD5lxgBHMsjrGwWWQ'

    soup = soup_channel(chan_serial)
    script = select_script_tag(soup)
    json_data = process_script(script)

    vids = get_video_items(json_data)
    cont = get_cont_token(json_data)

    idx = 0
    while True:
        resp = soup_next_page(cont)
        json_data = json.loads(resp.text)

        items = get_video_items_cont(json_data)
        vids.extend(items)

        cont = get_cont_token_cont(json_data)
        print(len(vids))
        idx = idx + 1


main()