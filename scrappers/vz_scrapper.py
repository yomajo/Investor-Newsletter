from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup


class VzScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within VZSCRAPPER in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
        
    def get_category_feature_article(self, content_container, appendable_output_list):
        '''appends second arg with single list of feature article headline and url from passed content container'''
        feature_article_headline = content_container.find('div', class_='main-article').h2.a.text
        feature_article_url_unval = content_container.find('div', class_='main-article').h2.a['href']
        feature_article_url = self.validate_url(feature_article_url_unval)
        cat_feature_list = [feature_article_headline, feature_article_url]
        appendable_output_list.append(cat_feature_list)        

    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        all_category_divs = content_container.findAll('div', class_='article')
        for article_div in all_category_divs:
            article_headline_raw = article_div.h2.a.text.strip()    
            article_headline = self.clean_headline(article_headline_raw)
            article_url_unval = article_div.h2.a['href']
            article_url = self.validate_url(article_url_unval)
            cycle_output_as_list = [article_headline, article_url]
            appendable_output_list.append(cycle_output_as_list)

    def clean_headline(self, headline):
        '''removes tabs, newline, other non-interest symbols'''
        repl_headline = headline.replace('\tPremium','').replace('\xa0','').replace('\r', '').replace('\n', '').replace('\t', '')
        cleaned_headline = repl_headline.strip()
        return cleaned_headline

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category response'''
        if response != None:
            self.category_results = []
            self.content_container = self.get_content_container(response, 'div', 'main')
            self.get_category_feature_article(self.content_container, self.category_results)
            self.get_category_articles(self.content_container, self.category_results)
        else:
            print('Server did not respond well')
        

if  __name__ == '__main__':
    pass