import requests
import tqdm
import re
import logging


class LastFMApi():
    API_KEY = 'api_key :)'
    API_URL = 'https://ws.audioscrobbler.com'
    chart_gettoptracks = API_URL + '/2.0/?method=chart.gettoptracks&api_key={api_key}&format=json&limit={limit}&page={page}'
    geo_gettoptracks = API_URL + '/2.0/?method=geo.gettoptracks&country={country}&api_key={api_key}&format=json&limit={limit}&page={page}'
    track_getInfo = API_URL + '/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track}&format=json'
    tag_getInfo = API_URL + '/2.0/?method=tag.getInfo&api_key={api_key}&tag={tag}&format=json'
    album_getInfo = API_URL + '/2.0/?method=album.getinfo&api_key={api_key}&artist={artist}&album={album}&format=json'

    decade_pattern_short = r'^\d{2}s$'
    decade_pattern = r'^\d{4}s$'
    year_pattern = r'^\d{4}$'
    forbidden_tags = ['MySpotigramBot']
    decade_conversion = {'20s' : '20', '10s': '20', '00s': '20'}

    pages_default = 100
    limit_default = 1000

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.cached_responses = {}

    def safe_get(self, data, keys, default=None):
        try:
            result = data
            for key in keys:
                result = result[key]
            return result
        except:
            if self.verbose:
                logging.warning('got safe_get exception')
            return default

    def get_response(self, url):
        if url in self.cached_responses:
            return self.cached_responses[url]
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                if 'error' in data:
                    if self.verbose:
                        logging.info('got error in data')
                    return None
                self.cached_responses[url] = response.json()
                return data
            except:
                pass
        if self.verbose:
            logging.warning('got bad response')
        return None


    def get_top_chart(self, pages=pages_default, limit=limit_default):
        data = []
        idx = 1
        for page in tqdm.tqdm(range(pages)):
            endpoint = self.chart_gettoptracks.format(api_key=self.API_KEY, limit=limit, page=page + 1)
            response = self.get_response(endpoint)
            if len(response['tracks']['track']) == 0:
                if self.verbose:
                    logging.info('last page reached')
                break
            for track in self.safe_get(response, ['tracks', 'track'], []):
                track_name = self.safe_get(track, ['name'])
                artist = self.safe_get(track, ['artist', 'name'])
                listeners = self.safe_get(track, ['listeners'])
                data.append({
                    'track_name': track_name,
                    'artist': artist,
                    'listeners': listeners,
                    'position': idx,
                })
                idx += 1
        return data


    def get_top_chart_by_country(self, country, pages=pages_default, limit=limit_default):
        data = []
        idx = 1
        for page in tqdm.tqdm(range(pages)):
            endpoint = self.geo_gettoptracks.format(country=country, api_key=self.API_KEY, limit=limit, page=page + 1)
            response = self.get_response(endpoint)
            if len(self.safe_get(response, ['tracks', 'track'], [])) == 0:
                if self.verbose:
                    logging.info('last page reached')
                break
            country_code = country.lower().replace(' ', '_')
            for track in self.safe_get(response, ['tracks', 'track'], []):
                track_name = self.safe_get(track, ['name'])
                artist = self.safe_get(track, ['artist', 'name'])
                listeners = self.safe_get(track, ['listeners'])
                data.append({
                    'track_name': track_name,
                    'artist': artist,
                    'listeners': listeners,
                    '{}_position'.format(country_code): idx,
                })
                idx += 1
        return data


    def get_track_info(self, artist, track):
        endpoint = self.track_getInfo.format(artist=artist, track=track, api_key=self.API_KEY)
        response = self.get_response(endpoint)
        playcount = self.safe_get(response, ['track', 'playcount'])
        toptag = self.safe_get(response, ['track', 'toptags', 'tag', 0, 'name'])
        if toptag in self.forbidden_tags:
            toptag = self.safe_get(response, ['track', 'toptags', 'tag', 1, 'name'])
        album = self.safe_get(response, ['track', 'album', 'title'])
        data = {
            'playcount': playcount,
            'toptag': toptag,
            'album': album,
        }
        return data


    def get_tag_info(self, tag):
        endpoint = self.tag_getInfo.format(tag=tag, api_key=self.API_KEY)
        response = self.get_response(endpoint)
        tag_summary = self.safe_get(response, ['tag', 'wiki', 'summary'])
        data = {
            'tag_summary': tag_summary,
        }
        return data


    def get_album_info(self, artist, album):
        endpoint = self.album_getInfo.format(artist=artist, album=album, api_key=self.API_KEY)
        response = self.get_response(endpoint)
        decade = '2020s'
        name = self.safe_get(response, ['album', 'name'])
        for tag in self.safe_get(response, ['album', 'tags', 'tag'], []):
            if not isinstance(tag, list):
                continue
            if re.match(self.decade_pattern_short, tag['name']):
                decade = self.decade_conversion.get(tag, '19') + tag
                break
            if re.match(self.decade_pattern, tag['name']):
                decade = tag
                break
            if re.match(self.year_pattern, tag['name']):
                year = int(tag['name'])
                decade = str(year - year % 10) + 's'
                break
        data = {
            'decade': decade,
            'name': name,
        }
        return data
