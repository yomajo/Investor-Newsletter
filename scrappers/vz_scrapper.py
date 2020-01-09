from bs4 import BeautifulSoup
from configparser import ConfigParser
from time import sleep
from random import randint
import os
import requests
import lxml
import csv

# Functions to extract data from soup and clean data
def get_category_main_article(content_container):
    '''returns list of main article headline and url from passed soup'''
    main_cat_url = content_container.find('div', class_='main-article').h2.a['href']
    main_cat_headline = content_container.find('div', class_='main-article').h2.a.text
    return [main_cat_headline, main_cat_url]

def get_category_articles(content_container, appendable_output_list):
    '''returns list of main article headline and url from passed soup'''
    all_category_divs = content_container.findAll('div', class_='article')
    for article_div in all_category_divs:
        article_headline_raw = article_div.h2.a.text.strip()    
        article_headline = clean_headline(article_headline_raw)
        article_url = article_div.h2.a['href']
        cycle_output_as_list = [article_headline, article_url]
        appendable_output_list.append(cycle_output_as_list)

def clean_headline(headline):
    '''removes tabs, newline, other non-interest symbols'''
    repl_headline = headline.replace('\tPremium','').replace('\xa0','').replace('\r', '').replace('\n', '').replace('\t', '')
    cleaned_headline = repl_headline.strip()
    return cleaned_headline


class VzScrapper():
    '''Verslo zinios scrapper class. Reads url categories from config.ini,
    outputs scrape results to txt file'''
    
    base_url = 'https://www.vz.lt/'
    config_file = 'scrappers/config.ini'
    outputfile = 'Output/vz_headlines.csv'

    def __init__(self):
        pass

    def get_categs_list(self):
        '''return list of categories (string as part of url)'''
        categs = []
        # Read contents under class named section in config.ini
        config = ConfigParser()
        config.read(self.config_file)        
        raw_cls_config = config.items(f'{self.__class__.__name__.upper()}')
        for _, cat in raw_cls_config:
            categs.append(cat)
        return categs
    
    def get_urls(self):
        '''returns ready urls'''
        categs = self.get_categs_list()
        urls_list = []
        for cat in categs:
            urls_list.append(self.base_url + cat) 
        return urls_list

    def get_response(self, url):
        '''checks passsed url and returns response if available'''
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r
        else:
            print(f'While passing url: {url} server responded with code: {r.status_code}.')
            return None

    def scrape_category(self, response):
        '''collects links and article headlines within passed category url'''
        if response != None:
            self.category_results = []
            self.soup = BeautifulSoup(response.content, 'lxml')
            self.content_container = self.soup.find('div', class_='main')

            main_article_data = get_category_main_article(self.content_container)
            self.category_results.append(main_article_data)
            get_category_articles(self.content_container, self.category_results)

    def export_csv(self, output_filename, output_data, w_a_option):
        '''write output contents to csv file'''
        with open(output_filename, w_a_option, newline='') as f:
            csv_writer = csv.writer(f, delimiter='\t')
            for headline_info in output_data:
                csv_writer.writerow(headline_info)
    
    def write_or_append_output(self, output_filepath):
        '''Check if output file exists and return according option for with-open context manager'''
        if os.path.exists(output_filepath):
            return 'a'
        else:
            return 'w'

    def run(self):
        '''main method upon instance creation'''
        urls_list = self.get_urls()
        print(f'Collected category urls:\n{urls_list}')
        self.unique_headlines_list = []
        for url in urls_list:
            print('-----------New category request---------')
            response = self.get_response(url)
            self.scrape_category(response)
            # Transfer from category to common variable holding unique records in this website
            print('Writing category headlines infomation to common variable')
            for headline_info in self.category_results:
                if headline_info not in self.unique_headlines_list:
                    self.unique_headlines_list.append(headline_info)

            print(f'\nServer response time: {response.elapsed.total_seconds()}')
            print('sleeping before jumping to next category... ZZZzzzz...')
            sleep(randint(10, 40)/10)

        # Exporting scrape results after loop through categories:
        w_a_option = self.write_or_append_output(self.outputfile)
        self.export_csv(self.outputfile, self.unique_headlines_list, w_a_option)

if  __name__ == '__main__':
    pass