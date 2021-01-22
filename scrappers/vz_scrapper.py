from utils import download_img, USER_AGENTS
from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class VzScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within VZSCRAPPER in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    
    Main method .get_website_data() returns list of dicts with unique headline data'''
        
    def get_category_feature_article(self, content_container:object, category:str):
        '''scrapes feature article data within category content_container if url not yet in self.unique_urls_set.
        Appends headline data dict to self.website_data list'''
        try:
            # article url
            feature_article_url_unval = content_container.find('div', class_='main-article').h2.a['href']
            feature_article_url = self.validate_url(feature_article_url_unval)
            
            if feature_article_url not in self.unique_urls_set:
                self.unique_urls_set.add(feature_article_url)
                # headline
                feature_article_headline_raw = content_container.find('div', class_='main-article').h2.a.text
                feature_article_headline = self.__clean_headline(feature_article_headline_raw)
                
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

    def get_category_articles(self, content_container:object, category:str):
        '''scrapes articles data within category content_container if urls not yet in self.unique_urls_set.
        Appends headline data dicts to self.website_data list'''
        try:    
            all_category_divs = content_container.findAll('div', class_='article')
            for article_div in all_category_divs:
                # article url
                article_url_unval = article_div.h2.a['href']
                article_url = self.validate_url(article_url_unval)
                
                if article_url not in self.unique_urls_set:
                    self.unique_urls_set.add(article_url)
                    # headline
                    article_headline_raw = article_div.h2.a.text.strip()    
                    article_headline = self.__clean_headline(article_headline_raw)
                    
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

    @staticmethod
    def __clean_headline(headline:str) -> str:
        '''removes tabs, newline, other non-interest symbols'''
        repl_headline = headline.replace('\tPremium','').replace('\xa0','').replace('\r', '').replace('\n', '').replace('\t', '')
        cleaned_headline = repl_headline.strip()
        return cleaned_headline


if  __name__ == '__main__':
    pass