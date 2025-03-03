import requests
import pandas as pd
import time
import tqdm
import re


class LastFMApi():
    API_KEY = 'api_key :)'
    API_URL = 'https://ws.audioscrobbler.com'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    chart_gettoptracks = API_URL + '/2.0/?method=chart.gettoptracks&api_key={api_key}&format=json&limit={limit}&page={page}'
    geo_gettoptracks = API_URL + '/2.0/?method=geo.gettoptracks&country={country}&api_key={api_key}&format=json&limit={limit}&page={page}'
    track_getInfo = API_URL + '/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track}&format=json'
    tag_getInfo = API_URL + '/2.0/?method=tag.getInfo&api_key={api_key}&tag={tag}&format=json'
    album_getInfo = API_URL + '/2.0/?method=album.getinfo&api_key={api_key}&artist={artist}&album={album}&format=json'

    decade_pattern = r'^\d{2}s$'
    year_pattern = r'^\d{4}$'

    pages_default = 100
    limit_default = 1000

    def __init__(self):
        self.cached_responses = {}

    def get_response(self, url):
        if url in self.cached_responses:
            return self.cached_responses[url]
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                return None
            print('update cache')
            self.cached_responses[url] = response.json()
            return data
        else:
            print(f'Ошибка {response.status_code}: {response.text}')
        return None


    def get_top_chart(self, pages=pages_default, limit=limit_default):
        data = []
        for page in tqdm.tqdm(range(pages)):
            endpoint = self.chart_gettoptracks.format(api_key=self.API_KEY, limit=limit, page=page + 1)
            response = self.get_response(endpoint)
            if not response:
                continue
            for idx, track in enumerate(response['tracks']['track']):
                data.append({
                    'track_name': track['name'],
                    'artist': track['artist']['name'],
                    'listeners': track.get('listeners', '-'),
                    'position': page * limit + idx,
                })
        return data


    def get_top_chart_by_country(self, country, pages=pages_default, limit=limit_default):
        data = []
        for page in tqdm.tqdm(range(pages)):
            endpoint = self.geo_gettoptracks.format(country=country, api_key=self.API_KEY, limit=limit, page=page + 1)
            response = self.get_response(endpoint)
            if not response:
                continue
            country_code = country.lower().replace(' ', '_')
            for idx, track in enumerate(response['tracks']['track']):
                data.append({
                    'track_name': track['name'],
                    'artist': track['artist']['name'],
                    'listeners': track.get('listeners', '-'),
                    '{}_position'.format(country): page * limit + idx,
                })
        return data


    def get_track_info(self, artist, track):
        endpoint = self.track_getInfo.format(artist=artist, track=track, api_key=self.API_KEY)
        response = self.get_response(endpoint)
        if not response:
            return {}
        data = {
            'playcount': response['track']['playcount'],
            'toptag': response['track']['toptags']['tag'][0]['name'],
        }
        return data


    def get_tag_info(self, tag):
        endpoint = self.tag_getInfo.format(tag=tag, api_key=self.API_KEY)
        response = self.get_response(endpoint)
        if not response:
            return {}
        data = {
            'tag_summary': response['tag']['wiki']['summary'],
        }
        return data


    def get_album_info(self, artist, album):
        endpoint = self.album_getInfo.format(artist=artist, album=album, api_key=self.API_KEY)
        response = self.get_response(endpoint)
        if not response:
            return {}
        decade = None
        for tag in response['album']['tags']['tag']:
            if re.match(self.decade_pattern, tag['name']):
                decade = tag
                break
            if re.match(self.year_pattern, tag['name']):
                year = int(tag['name'])
                decade = str((year - year % 10) % 100) + 's'
                break
        data = {
            'decade': decade,
            'name': response['album']['name'],
        }
        return data
