from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup


class LrtScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within LrtScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
        
    def get_category_feature_article(self, content_container, appendable_output_list):
        '''appends second arg with single list of feature article headline and url from passed content container'''
        feature_article_container = content_container.find('div', class_='section-news-rubric__top col-12')
        feature_headline = feature_article_container.h3.a.text
        feature_url_unval = feature_article_container.h3.a['href']
        feature_url = self.validate_url(feature_url_unval)
        cat_feature_list = [feature_headline, feature_url]
        appendable_output_list.append(cat_feature_list)
        
    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        all_category_divs = content_container.find('div', id='category_list')
        article_containers = all_category_divs.findAll('h3', class_='news__title')
        for article in article_containers:
            article_headline = article.a.text.strip()
            article_url_unval = article.a['href']
            article_url = self.validate_url(article_url_unval)
            cycle_output_as_list = [article_headline, article_url]
            appendable_output_list.append(cycle_output_as_list)

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category response'''
        if response != None:
            self.category_results = []
            # Pass corresponding html element and CSS class to  
            self.content_container = self.get_content_container(response, 'div', 'section-news-rubric__grid row')
            self.get_category_feature_article(self.content_container, self.category_results)
            self.get_category_articles(self.content_container, self.category_results)
        else:
            print('Server did not respond well')
        

if  __name__ == '__main__':
    pass