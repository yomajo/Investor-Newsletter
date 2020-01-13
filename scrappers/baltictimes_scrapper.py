from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup


class BalticTimesScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within LrtScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
        
    def get_category_feature_article(self, content_container, appendable_output_list):
        '''appends second arg with single list of feature article headline and url from passed content container'''
        feature_article_container = content_container.find('div', class_='row portfolio-item')
        feature_artcle_headline = feature_article_container.find('div', class_='col-md-5')
        feature_headline = feature_artcle_headline.h2.text
        feature_url = feature_artcle_headline.a['href']
        cat_feature_list = [feature_headline, feature_url]
        appendable_output_list.append(cat_feature_list)
        
    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        rest_articles_wrapper = content_container.find('div', id='tbt-mobile-front')
        article_containers = rest_articles_wrapper.findAll('div', class_='row blog blog-medium margin-bottom-20')
        for article in article_containers:
            article_headline = article.h4.text
            article_url = article.a['href']
            cycle_output_as_list = [article_headline, article_url]
            appendable_output_list.append(cycle_output_as_list)

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category response'''
        if response != None:
            self.category_results = []
            self.content_container = self.get_content_container(response)
            self.get_category_feature_article(self.content_container, self.category_results)
            self.get_category_articles(self.content_container, self.category_results)
        else:
            print('Server did not respond well')
    
    def get_content_container(self, response):
        '''returns main articles holding container of html soup object'''
        self.soup = BeautifulSoup(response.content, 'lxml')
        content_container_raw = self.soup.find('div', class_='row magazine-page tbt-bg')
        self.content_container = content_container_raw.find('div', class_='col-md-9')
        return self.content_container
        

if  __name__ == '__main__':
    pass