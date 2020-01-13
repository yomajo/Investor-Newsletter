from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup


class PostimeesScrapper(Scrapper):
    '''Modifying inherited structure to scrape ECONOMY category SEARCH PAGE within PostimeesScrapper in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
        
    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        all_category_divs = content_container.findAll('li', class_='search-results__item')
        for article in all_category_divs:
            article_headline = article.span.a.text.strip()
            article_url = article.span.a['href']
            cycle_output_as_list = [article_headline, article_url]
            appendable_output_list.append(cycle_output_as_list)

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category respose'''
        if response != None:
            self.category_results = []
            self.content_container = self.get_content_container(response, 'ul', 'search-results')
            self.get_category_articles(self.content_container, self.category_results)
        else:
            print('Server did not respond well')
        

if  __name__ == '__main__':
    pass