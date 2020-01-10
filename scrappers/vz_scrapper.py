from scrappers.scrapper import Scrapper
from bs4 import BeautifulSoup


class VzScrapper(Scrapper):
    '''Modifying inherited structure to scrape categories within VZSCRAPPER in config.ini. Instance takes args:
    - base website
    - path to config file where class takes website categories suffix to url
    - relative output csv file path'''
    
    def get_content_container(self, response, html_element, css_class):
        '''returns main articles holding container of html soup object'''
        self.soup = BeautifulSoup(response.content, 'lxml')
        self.content_container = self.soup.find(html_element, class_=css_class)
        return self.content_container
    
    def get_category_feature_article(self, content_container, appendable_output_list):
        '''appends second arg with single list of feature article headline and url from passed content container'''
        main_cat_headline = content_container.find('div', class_='main-article').h2.a.text
        main_cat_url = content_container.find('div', class_='main-article').h2.a['href']
        cat_feature_list = [main_cat_headline, main_cat_url]
        appendable_output_list.append(cat_feature_list)        

    def get_category_articles(self, content_container, appendable_output_list):
        '''appends second arg with list of article headlines and urls from passed content container'''
        all_category_divs = content_container.findAll('div', class_='article')
        for article_div in all_category_divs:
            article_headline_raw = article_div.h2.a.text.strip()    
            article_headline = self.clean_headline(article_headline_raw)
            article_url = article_div.h2.a['href']
            cycle_output_as_list = [article_headline, article_url]
            appendable_output_list.append(cycle_output_as_list)

    def clean_headline(self, headline):
        '''removes tabs, newline, other non-interest symbols'''
        repl_headline = headline.replace('\tPremium','').replace('\xa0','').replace('\r', '').replace('\n', '').replace('\t', '')
        cleaned_headline = repl_headline.strip()
        return cleaned_headline

    def scrape_category(self, response):
        '''Collects links and article headlines within passed category url'''
        if response != None:
            self.category_results = []
            # Pass corresponding html element and CSS class to  
            self.content_container = self.get_content_container(response, 'div', 'main')
            self.get_category_feature_article(self.content_container, self.category_results)
            self.get_category_articles(self.content_container, self.category_results)
        else:
            print('Server did not respond well')
        

if  __name__ == '__main__':
    pass