import requests
from bs4 import BeautifulSoup
import logging
import tqdm

class GenreScraper():

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    genre_url_tmpl = 'https://www.chosic.com/genre-chart/{}/'
    basic_genres_tmpl = 'https://www.chosic.com/list-of-music-genres/'
    cached_responses = {}

    def __init__(self, verbose=True):
        self.weights = {}
        self.verbose = verbose
        if self.verbose:
            logging.info('start init...')
        subset = self.get_basic_genres()
        popularity_data = {}
        for element in tqdm.tqdm(subset, disable=not self.verbose):
            decade_data = self.get_genre_popularity(genre=element, verbose=False)
            for decade in decade_data:
                if decade not in popularity_data:
                    popularity_data[decade] = []
                popularity_data[decade].append(decade_data[decade])
        for decade in popularity_data:
            self.weights[decade] = sum(popularity_data[decade]) / len(popularity_data)
        if self.verbose:
            logging.info('successfully initialized')

    def get_response(self, url):
        if url in self.cached_responses:
            return self.cached_responses[url]
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            self.cached_responses[url] = response
        else:
            logging.warn('got response with code: {}'.format(response.status_code))
        return response

    def get_genre_stats_url(self, genre):
        genre_pretty = '-'.join(genre.lower().replace('&', '').split('/')[0].split())
        return self.genre_url_tmpl.format(genre_pretty)

    def get_basic_genres(self, verbose=True):
        verbose &= self.verbose
        if verbose:
            logging.info('run basic genres request')
        response = self.get_response(self.basic_genres_tmpl)
        html_content = response.text
        if verbose:
            logging.info('got response with status: {}'.format(response.status_code))
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all(class_='tag-cloud-link')
        if verbose:
            logging.info('found {} genres'.format(len(links)))
        return [link.get('data-tag').lower() for link in links]

    def get_genre_popularity(self, genre, weighted=0, verbose=True):
        if not genre:
            return {}
        verbose &= self.verbose
        url = self.get_genre_stats_url(genre)
        if verbose:
            logging.info('run genre popularity request')
        response = self.get_response(url)
        html_content = response.text
        if verbose:
            logging.info('got response with status: {}'.format(response.status_code))
        if verbose:
            logging.info('start parsing')
        soup = BeautifulSoup(html_content, 'html.parser')
        decade_elements = soup.find_all('div', class_='text-bar-decade')

        decades_data = {}

        for element in tqdm.tqdm(decade_elements, disable=not verbose):
            decade_text = element.find('div', class_='progressbar-text').get_text().strip()
            decade_name = decade_text.split()[0]
            weight = [1, self.weights.get(decade_name, 1)][weighted]
            count = int(element.find('span', class_='albums-count').text) / weight
            decades_data[decade_name] = round(count, 3)

        return decades_data

    def get_genre_popularity_by_decade(self, genre, decade, weighted=0):
        if not genre:
            return None
        decades_data = self.get_genre_popularity(genre, weighted)
        return decades_data.get(decade, None)

    def get_genre_popularity_by_year(self, genre, year, weighted=0):
        if not genre:
            return None
        decades_data = self.get_genre_popularity(genre, weighted)
        decade = str(year - year % 10) + 's'
        return decades_data.get(decade, None)
