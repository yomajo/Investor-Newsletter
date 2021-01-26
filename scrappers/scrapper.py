from utils import get_user_agent_dict, download_img
from utils import USER_AGENTS
from configparser import ConfigParser
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import requests
import logging
import lxml
import os

# Initializing logging in module
logger = logging.getLogger(__name__)

class Scrapper():
    '''Generic Scrapper class indented to inherit from for each specific website scrapping class. Instance arguments:
    - base website
    - path to config file where class takes website categories suffix to url
    
    Functions that most likely need overwrite:
    - scrape_category
    - get_content_container
    - get_category_feature_article
    - get_category_articles
    
    Output unque scrape results as list of dicts with --> .get_website_data()
    urls are collected to self.unique_urls_set. Only new urls and rest of data
    
    returns a list (self.website_data) of headline data dicts. Example of single headline data:
            headline_data_dict = {
                    'headline':article_headline,
                    'category':category,
                    'url':article_url,
                    'img_url':article_img_url,
                    'img_path':img_path}'''

    def __init__(self, base_url, config_file):
        self.base_url = base_url
        self.config_file = config_file
        self.user_agent = get_user_agent_dict(USER_AGENTS)
        self.encoding = self.get_website_encoding()
        self.website_data = []
        self.unique_urls_set = set()

    def get_website_encoding(self):
        '''every website uses charset utf-8 except for vz.lt; returning encoding based on cls name'''
        if 'VZ' in self.__class__.__name__.upper():
            return 'Windows-1257'
        return 'utf-8'
            
    def get_urls(self) -> dict:
        '''returns ready [category] = category_url dict of urls to scrape from'''
        categ_url_dict = self.get_categs_dict()
        for cat in categ_url_dict.keys():
            categ_url_dict[cat] = self.base_url + categ_url_dict[cat] 
        return categ_url_dict

    def get_categs_dict(self) -> dict:
        '''return dict of category - category sub url pairs (dict value  as part of url string)'''
        cat_url_dict = {}
        class_name = self.__class__.__name__.upper()
        config = ConfigParser()
        config.read(self.config_file)
        logger.info(f'Reading config file {self.config_file} contents from section: {class_name}')        
        # Read contents under class named section in config.ini
        raw_cls_config = config.items(class_name)
        for cat, cat_suburl in raw_cls_config:
            cat_url_dict[cat] = cat_suburl
        return cat_url_dict

    def validate_url(self, url:str) -> str:
        '''converts relative url to absolute if neccesarry. self.base_url neccessary'''
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        else:
            return url

    def get_response(self, url) -> object:
        '''checks passsed url and returns response if available'''
        r = requests.get(url, headers=self.user_agent, timeout=10)
        if r.status_code == 200:
            return r
        else:
            logger.exception(f'Server did not respond well. Response code: {r.status_code} while accessing {url}')
            raise ConnectionError('Server response not 200. Check log exception for status code and url')

    def scrape_category(self, response:object, category:str):
        '''---OVERWRITE WHEN INHERITING---'''
        '''Collects headline data to cls variable self.website_data for passed response obj (category specific)'''
        if response != None:
            content_container = self.get_content_container(response, 'div', 'main')
            self.get_category_feature_article(content_container, category)
            self.get_category_articles(content_container, category)
        else:
            logger.error('Server did not respond well')

    def get_content_container(self, response:object, html_element:str, css_class:str) -> object:
        '''---OVERWRITE WHEN INHERITING---'''
        '''returns main html container (soup object) holding articles'''
        soup = BeautifulSoup(response.content, 'lxml', from_encoding=self.encoding)
        content_container = soup.find(html_element, class_=css_class)
        return content_container
    
    def get_category_feature_article(self, content_container:object, category:str):
        '''---OVERWRITE WHEN INHERITING---'''
        '''scrapes feature article data within category content_container if url not yet in self.unique_urls_set.
        Appends headline data dict to self.website_data list'''
        # try:
        #     # article url
        #     feature_article_url_unval = content_container.find('div', class_='main-article').h2.a['href']
        #     feature_article_url = self.validate_url(feature_article_url_unval)
            
        #     if feature_article_url not in self.unique_urls_set:
        #         self.unique_urls_set.add(feature_article_url)
        #         # headline
        #         feature_article_headline = content_container.find('div', class_='main-article').h2.a.text
                
        #         # article img url
        #         feature_article_img_url = self.validate_url(content_container.img['src'])
        #         img_path = download_img(feature_article_img_url, self.user_agent)
        #         headline_data_dict = {
        #                         'headline':feature_article_headline,
        #                         'category':category,
        #                         'url':feature_article_url,
        #                         'img_url':feature_article_img_url,
        #                         'img_path':img_path}
        #         self.website_data.append(headline_data_dict)
        # except:
        #     logger.exception('Error getting featured article data in category. Check for WEBSITE STRUCTURE CHANGES')
        pass

    def get_category_articles(self, content_container:object, category:str):
        '''---OVERWRITE WHEN INHERITING---'''
        '''scrapes articles data within category content_container if urls not yet in self.unique_urls_set.
        Appends headline data dicts to self.website_data list'''
        # try:    
        #     all_category_divs = content_container.findAll('div', class_='article')
        #     for article_div in all_category_divs:
        #         # article url
        #         article_url_unval = article_div.h2.a['href']
        #         article_url = self.validate_url(article_url_unval)
                
        #         if article_url not in self.unique_urls_set:
        #             self.unique_urls_set.add(article_url)
        #             # headline
        #             article_headline = article_div.h2.a.text.strip()    
                    
        #             # article img url
        #             try:
        #                 img_url = self.validate_url(article_div.img['src'])
        #                 img_path = download_img(img_url, self.user_agent)
        #             except TypeError:
        #                 logger.debug(f'Could not get img url for this article: {article_url} Returning \'#N/A\'')
        #                 img_url = img_path = '#N/A'
        #             headline_data_dict = {
        #                         'headline':article_headline,
        #                         'category':category,
        #                         'url':article_url,
        #                         'img_url':img_url,
        #                         'img_path':img_path}
        #             self.website_data.append(headline_data_dict)
        # except:
        #     logger.exception('Error grabbing category articles. Check for WEBSITE STRUCTURE CHANGES')
        pass
        
    def get_website_data(self) -> list:
        '''iterates over category urls, scrapes data from each category, returns a list of dicts of unique (cls/website/scrape run scope)
        headline data'''
        category_urls = self.get_urls()
        for category, category_url in category_urls.items():
            logger.info(f'New request for category: {category}, url: {category_url}')
            response = self.get_response(category_url)
            logger.info(f'Server response time: {response.elapsed.total_seconds()}')
            self.scrape_category(response, category)
            logging.info('sleeping before jumping to next category... ZZzz...')
            sleep(randint(10, 50)/10)
        logger.info(f'Returning {len(self.website_data)} headlines from {self.__class__.__name__}')
        return self.website_data


if  __name__ == '__main__':
    pass