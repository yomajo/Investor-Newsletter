from bs4 import BeautifulSoup
from configparser import ConfigParser
from time import sleep
from random import randint
from urllib.parse import urljoin
import os
import requests
import lxml
import csv
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

# User Agent for Requests
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

class Scrapper():
    '''Generic Scrapper class indented to inherit from for each specific website. Instance arguments:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path
    
    Functions that most likely need overwrite:
    - scrape_category
    - get_content_container
    - get_category_feature_article
    - get_category_articles
    
    Once ready --> get_website_headlines_as_list()
    Output export --> export_list_to_csv(args*)
    '''

    def __init__(self, base_url, config_file):
        self.base_url = base_url
        self.config_file = config_file

    def get_categs_list(self):
        '''return list of categories (string as part of url)'''
        categs = []
        # Read contents under class named section in config.ini
        config = ConfigParser()
        config.read(self.config_file)
        logger.info(f'Reading config file {self.config_file} contents from section: {self.__class__.__name__.upper()}')        
        raw_cls_config = config.items(f'{self.__class__.__name__.upper()}')
        for _, cat in raw_cls_config:
            categs.append(cat)
        return categs
    
    def get_urls(self):
        '''returns ready urls'''
        self.categs = self.get_categs_list()
        self.urls_list = []
        for cat in self.categs:
            self.urls_list.append(self.base_url + cat) 
        return self.urls_list

    def get_response(self, url):
        '''checks passsed url and returns response if available'''
        r = requests.get(url, timeout=10, headers=HEADERS)
        if r.status_code == 200:
            return r
        else:
            logger.exception(f'Server did not respond well. Response code: {r.status_code} while accessing {url}')
            raise Exception

    def scrape_category(self, response):
        '''---OVERWRITE WHEN INHERITING---'''
        '''collects links and article headlines within passed category response'''
        self.category_results = []
        # # Pass corresponding html element and CSS class to
        # self.content_container = self.get_content_container(response, 'HTML_ELEMENT', 'CSS_CLASS')
        # feature_article_data = get_category_feature_article(self.content_container)
        # self.category_results.append(feature_article_data)
        # get_category_articles(self.content_container, self.category_results)

    def get_content_container(self, response, html_element, css_class):
        '''---OVERWRITE WHEN INHERITING---'''
        '''returns main articles holding container of html soup object'''
        self.soup = BeautifulSoup(response.content, 'lxml')
        self.content_container = self.soup.find(html_element, class_=css_class)
        return self.content_container
    
    def get_category_feature_article(self, content_container):
        '''---OVERWRITE WHEN INHERITING---'''
        '''appends second arg with single list of feature article headline and url from passed content container'''
        pass

    def get_category_articles(self, content_container, appendable_output_list):
        '''---OVERWRITE WHEN INHERITING---'''
        '''appends second arg with list of article headlines and urls from passed content container'''
        pass

    def validate_url(self, url):
        '''converts relative url to absolute if neccesarry. self.base_url neccessary'''
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        else:
            return url

    def get_website_headlines_as_list(self):
        '''iterates over category urls, scrapes data from each category, returns a list of lists of unique headlines and urls'''
        self.get_urls()
        self.unique_headlines_list = []
        for idx, url in enumerate(self.urls_list):
            logger.info(f'New request for category: {self.categs[idx]}')
            response = self.get_response(url)
            logger.info(f'Server response time: {response.elapsed.total_seconds()}')
            
            self.scrape_category(response)
            self.category_to_output_list(self.category_results, self.unique_headlines_list)

            logging.info('sleeping before jumping to next category... ZZzz...')
            sleep(randint(10, 50)/10)
        return self.unique_headlines_list

    def category_to_output_list(self, category_list, unique_records):
        '''takes input arg of category-level scrape results and transfers unique records to output list. Returns it
        (prevents same entry from different categories)'''
        logger.info('Writing category headlines infomation to common variable')
        for headline_info in category_list:
            if headline_info not in unique_records:
                unique_records.append(headline_info)
        return unique_records


if  __name__ == '__main__':
    pass