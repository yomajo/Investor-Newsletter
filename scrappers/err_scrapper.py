from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class ERRScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within ERRScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
        
    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        try:
            all_category_divs = content_container.findAll('div', class_='category-item')
            for article in all_category_divs:
                article_headline = article.p.a.text.strip()
                article_url_unval = article.p.a['href']
                article_url = self.validate_url(article_url_unval)
                cycle_output_as_list = [article_headline, article_url]
                appendable_output_list.append(cycle_output_as_list)
        except:
            logger.exception('Error grabbing category articles. Check for WEBSITE STRUCTURE CHANGES')

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category response'''
        if response != None:
            self.category_results = []
            self.content_container = self.get_content_container(response, 'div', 'left-block')
            self.get_category_articles(self.content_container, self.category_results)
        else:
            logger.error('Server did not respond well')
        

if  __name__ == '__main__':
    pass