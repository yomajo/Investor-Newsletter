from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class BalticTimesScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within LrtScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
        
    def get_category_feature_article(self, content_container, appendable_output_list):
        '''appends second arg with single list of feature article headline and url from passed content container'''
        try:
            feature_article_container = content_container.find('div', class_='row portfolio-item')
            feature_artcle_headline = feature_article_container.find('div', class_='col-md-5')
            feature_headline = feature_artcle_headline.h2.text
            feature_url_unval = feature_artcle_headline.a['href']
            feature_url = self.validate_url(feature_url_unval)
            cat_feature_list = [feature_headline, feature_url]
            appendable_output_list.append(cat_feature_list)
        except:
            logger.exception('Error getting featured article data in category. Check for WEBSITE STRUCTURE CHANGES')        

    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        try:
            rest_articles_wrapper = content_container.find('div', id='tbt-mobile-front')
            article_containers = rest_articles_wrapper.findAll('div', class_='row blog blog-medium margin-bottom-20')
            for article in article_containers:
                article_headline = article.h4.text
                article_url_unval = article.a['href']
                article_url = self.validate_url(article_url_unval)
                cycle_output_as_list = [article_headline, article_url]
                appendable_output_list.append(cycle_output_as_list)
        except:
            logger.exception('Error grabbing category articles. Check for WEBSITE STRUCTURE CHANGES')

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category response'''
        if response != None:
            self.category_results = []
            self.content_container = self.get_content_container(response)
            self.get_category_feature_article(self.content_container, self.category_results)
            self.get_category_articles(self.content_container, self.category_results)
        else:
            logger.error('Server did not respond well')
    
    def get_content_container(self, response):
        '''returns main articles holding container of html soup object'''
        try:
            self.soup = BeautifulSoup(response.content, 'lxml')
            content_container_raw = self.soup.find('div', class_='row magazine-page tbt-bg')
            self.content_container = content_container_raw.find('div', class_='col-md-9')
            return self.content_container
        except:
            logger.error('Error getting main content container. Check for WEBSITE STRUCTURE CHANGES')


if  __name__ == '__main__':
    pass