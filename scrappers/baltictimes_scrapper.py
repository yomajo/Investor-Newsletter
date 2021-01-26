from scrappers.scrapper import Scrapper
from utils import download_img
from bs4 import BeautifulSoup
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class BalticTimesScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within LrtScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url'''

    def scrape_category(self, response:object, category:str):
        '''Collects headline data to cls variable self.website_data for passed response obj (category specific)'''
        if response != None:
            content_container = self.get_content_container(response, 'div', 'tbt-main-container')
            self.get_category_feature_article(content_container, category)
            self.get_category_articles(content_container, category)
        else:
            logger.error('Server did not respond well')

    def get_content_container(self, response:object, html_element:str, css_id:str) -> object:
        '''---OVERWRITE WHEN INHERITING---'''
        '''returns main html container (soup object) holding articles'''
        soup = BeautifulSoup(response.content, 'lxml', from_encoding=self.encoding)
        content_container = soup.find(html_element, id=css_id)
        return content_container
        
    def get_category_feature_article(self, content_container:object, category:str):
        '''scrapes feature article data within category content_container if url not yet in self.unique_urls_set.
        Appends headline data dict to self.website_data list'''
        try:
            feature_div = content_container.find('div', class_='row portfolio-item')
            # article url
            feature_article_url_unval = feature_div.a['href']
            feature_article_url = self.validate_url(feature_article_url_unval)
            
            if feature_article_url not in self.unique_urls_set:
                self.unique_urls_set.add(feature_article_url)
                # headline
                feature_article_headline = feature_div.h2.text.strip()
                
                # article img url
                feature_article_img_url_raw = feature_div.find('img', class_='img-responsive')['src']
                feature_article_img_url = self.validate_url(feature_article_img_url_raw)
                img_path = download_img(feature_article_img_url, self.user_agent)
                headline_data_dict = {
                                'headline':feature_article_headline,
                                'category':category,
                                'url':feature_article_url,
                                'img_url':feature_article_img_url,
                                'img_path':img_path}
                self.website_data.append(headline_data_dict)
        except:
            logger.exception('Error getting featured article data in category. Check for WEBSITE STRUCTURE CHANGES')

    def get_category_articles(self, content_container:object, category:str):
        '''scrapes articles data within category content_container if urls not yet in self.unique_urls_set.
        Appends headline data dicts to self.website_data list'''
        try:    
            all_category_divs = content_container.findAll('div', class_='tbtthirdblock')
            for article_div in all_category_divs:
                # article url
                article_url_unval = article_div.a['href']
                article_url = self.validate_url(article_url_unval)
                
                if article_url not in self.unique_urls_set:
                    self.unique_urls_set.add(article_url)
                    # headline
                    article_headline = article_div.h5.text.strip()    
                    
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


if  __name__ == '__main__':
    pass