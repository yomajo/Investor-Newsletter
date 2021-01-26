from scrappers.scrapper import Scrapper
from utils import download_img
from bs4 import BeautifulSoup
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class DbScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within DBSCRAPPER in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url'''
        
    def get_category_feature_article(self, content_container:object, category:str):
        '''scrapes feature article data within category content_container if url not yet in self.unique_urls_set.
        Appends headline data dict to self.website_data list
        NOTE: Contains one main feature article and three sub-feature blocks, therefore multiple calls to feature article extraction'''
        try:
            # article url
            feature_article_url_unval = content_container.a['href']
            feature_article_url = self.validate_url(feature_article_url_unval)
            
            if feature_article_url not in self.unique_urls_set:
                self.unique_urls_set.add(feature_article_url)
                # headline
                feature_article_headline = content_container.h1.text.strip()
                
                # article img url
                feature_article_img_url = self.validate_url(content_container.img['src'])
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


    def get_category_articles(self, soup:object, category:str):
        '''scrapes articles data within category content_container if urls not yet in self.unique_urls_set.
        Appends headline data dicts to self.website_data list'''
        try:    
            all_category_divs = soup.findAll('div', class_='padding-2--bottom')
            for article_div in all_category_divs:
                # article url
                article_url_unval = article_div.a['href']
                article_url = self.validate_url(article_url_unval)
                
                if article_url not in self.unique_urls_set:
                    self.unique_urls_set.add(article_url)
                    # headline
                    article_headline = article_div.h1.text.strip()    
                    
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

    def get_content_container(self, response:object, html_element:str, css_class:str) -> object:
        '''returns both soup and main html container (soup object) holding articles'''
        soup = BeautifulSoup(response.content, 'lxml', from_encoding=self.encoding)
        content_container = soup.find(html_element, class_=css_class)
        return soup, content_container

    def scrape_category(self, response:object, category:str):
        '''Collects headline data to cls variable self.website_data for passed response obj (category specific)'''
        if response != None:
            soup, content_container = self.get_content_container(response, 'div', 'grid wrap grid-spacing--2')
            self.get_category_articles(soup, category)
            try:
                # Getting main feature article
                feature_article_div = content_container.find('div', class_='grid-cell-1-1')
                self.get_category_feature_article(feature_article_div, category)
                
                # Getting 3 sub-feature articles
                feature_article_divs = content_container.findAll('div', class_='grid-cell-1-3')
                for subfeature_div in feature_article_divs:
                    self.get_category_feature_article(subfeature_div, category)
            except Exception as e:
                logger.exception(f'Err: {e} while getting feature article div and sub feature divs container in DB scrapper')
                logger.warning('Failed to get DB feature articles, moving on with other articles...')
        else:
            logger.error('Server did not respond well')
        

if  __name__ == '__main__':
    pass