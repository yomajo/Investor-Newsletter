import requests
import logging
from time import sleep
import html

# Objects & Variables Initialization
logger = logging.getLogger(__name__)
API_URL_ESCAPING = 'http://api.icndb.com/jokes/random?exclude=[explicit,nerdy]?escape=javascript'

API_URL = 'http://api.icndb.com/jokes/random?exclude=[explicit,nerdy]'
CATEGORIES_URL = 'http://api.icndb.com/categories'


def add_joke_to_db(joke_id):
    '''TBD when database connections are in place'''
    # print(f'Adding id to db. ID: {joke_id}')
    pass

def get_chuck_norris_joke():
    '''return joke id, and random joke'''
    try:
        r = requests.get(API_URL_ESCAPING, timeout=5)
        r_json = r.json()
        raw_joke = r_json['value']['joke']
        joke = html.unescape(raw_joke)
        joke_id = r_json['value']['id']
        return joke_id, joke
    except:
        logger.warning('Chuck Norris API failed to provide a new joke. Returning hardcoded one instead')
        return 0, 'Chuck Norris entered a server hall. And that\'s no joke...'

def test_joke_fetching():
    for _ in range(5):
        joke_id, joke = get_chuck_norris_joke()
        add_joke_to_db(joke_id)
        sleep(2)
        print(f'ID: {joke_id}, joke: {joke}\n')

if __name__ == '__main__':
    # test_joke_fetching()
    pass