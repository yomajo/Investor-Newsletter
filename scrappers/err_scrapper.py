from scrappers.scrapper import Scrapper
from utils import download_img
from bs4 import BeautifulSoup
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class ERRScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within ERRScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    Note: ERR does not have feature articles, therefore no corresponding call to get_feature_article within category'''

    def get_category_articles(self, content_container:object, category:str):
        '''scrapes articles data within category content_container if urls not yet in self.unique_urls_set.
        Appends headline data dicts to self.website_data list'''
        try:    
            all_category_divs = content_container.findAll('div', class_='category-item')
            for article_div in all_category_divs:
                # article url
                article_url_unval = article_div.p.a['href']
                article_url = self.validate_url(article_url_unval)
                
                if article_url not in self.unique_urls_set:
                    self.unique_urls_set.add(article_url)
                    # headline
                    article_headline = article_div.p.a.text.strip()
                    
                    # article img url
                    try:
                        img_url = self.validate_url(article_div.img['src'])
                        img_path = download_img(img_url, self.user_agent)
                    except TypeError:
                        logger.debug(f'Could not get img url for this article: {article_url} Returning \'#N/A\'')
                        img_url = img_path = '#N/A'
                    headline_data_dict = {
                                'headline':article_headline,
                                'category':category,
                                'url':article_url,
                                'img_url':img_url,
                                'img_path':img_path}
                    self.website_data.append(headline_data_dict)
        except:
            logger.exception('Error grabbing category articles. Check for WEBSITE STRUCTURE CHANGES')

    def scrape_category(self, response:object, category:str):
        '''Collects headline data to cls variable self.website_data for passed response obj (category specific)'''
        if response != None:
            content_container = self.get_content_container(response, 'div', 'left-block')
            self.get_category_feature_article(content_container, category)
            self.get_category_articles(content_container, category)
        else:
            logger.error('Server did not respond well')


if  __name__ == '__main__':
    pass