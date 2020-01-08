from bs4 import BeautifulSoup
from configparser import ConfigParser
import requests
import lxml


def get_category_main_article(soup):
    '''returns tuple of headline and url from passed soup'''
    content_container = soup.find('div', class_='main')
    main_cat_url = content_container.find('div', class_='main-article').h2.a['href']
    main_cat_headline = content_container.find('div', class_='main-article').h2.a.text
    return (main_cat_headline, main_cat_url)


class VzScrapper():
    '''Verslo zinios scrapper class. Reads url categories from config.ini,
    outputs scrape results to txt file'''
    
    base_url = 'https://www.vz.lt/'
    config_file = 'scrappers/config.ini'

    def __init__(self):
        pass

    def get_categs_list(self):
        '''return list of categories (string as part of url)'''
        categs = []
        # Read contents under class section in config.ini
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

    def get_valid_response(self, url):
        '''checks passsed url for returns'''
        r = requests.get(url, timeout=5)
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
            main_article_data = get_category_main_article(self.soup)
            self.category_results.append(main_article_data)

    def run(self):
        '''main method upon instance creation'''
        urls_list = self.get_urls()
        print(f'Collected category urls:\n{urls_list}')

        for url in urls_list:
            response = self.get_valid_response(url)
            self.scrape_category(response)

            # temp print output:
            print(self.category_results)

            break





if  __name__ == '__main__':
    pass

