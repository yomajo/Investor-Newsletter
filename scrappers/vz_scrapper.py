from bs4 import BeautifulSoup
from configparser import ConfigParser
from time import sleep
from random import randint
import os
import requests
import lxml


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
    outputfile = 'Output/headlines.txt'

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
            self.soup = BeautifulSoup(response.text, 'lxml')
            self.content_container = self.soup.find('div', class_='main')

            main_article_data = get_category_main_article(self.content_container)
            self.category_results.append(main_article_data)
            get_category_articles(self.content_container, self.category_results)

    def export_txt(self, output_data, write_append_option):
        '''write output contents to txt file'''
        with open(self.outputfile, write_append_option) as f:
            for idx, headline_info in enumerate(output_data):
                # Handling new line for first item
                if idx:
                    # Not a first line, adding starting in newline
                    f.writelines(f'\n{str(headline_info[0])} {str(headline_info[1])}')
                elif write_append_option == 'a':
                    # Appending txt file. First line (idx==0), so new line for new entry before:
                    f.writelines(f'\n{str(headline_info[0])} {str(headline_info[1])}')
                else:
                    # First line in txt file:
                    f.writelines(f'{str(headline_info[0])} {str(headline_info[1])}')
    
    def write_or_append_output(self, txt_filepath):
        '''Check if output file exists and return according option for with-open context manager'''
        if os.path.exists(txt_filepath):
            return 'a'
        else:
            return 'w'

    def run(self):
        '''main method upon instance creation'''
        urls_list = self.get_urls()
        print(f'Collected category urls:\n{urls_list}')
        for url in urls_list:
            print('-----------New category request---------')
            response = self.get_response(url)
            self.scrape_category(response)

            # print('\nRESULTS FROM ONE CATEGORY-------------------BELOW-------------')
            # print(self.category_results)
            print(f'\nServer response time: {response.elapsed.total_seconds()}')
            # Exporting, now, in future, join from other categories:
            w_a_option = self.write_or_append_output(self.outputfile)
            self.export_txt(self.category_results, w_a_option)
            # temp print output:
            print('sleeping before jumping to next category... ZZZzzzz...')
            sleep(randint(10, 40)/10)
            # break

if  __name__ == '__main__':
    pass