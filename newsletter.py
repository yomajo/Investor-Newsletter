from scrappers.vz_scrapper import VzScrapper
from scrappers.lrt_scrapper import LrtScrapper
from scrappers.err_scrapper import ERRScrapper
from scrappers.postimees_scrapper import PostimeesScrapper
from scrappers.baltictimes_scrapper import BalticTimesScrapper
from scrappers.db_scrapper import DbScrapper
from translate import TranslateList
from configparser import ConfigParser

# GLOBAL VARIABLES:
CONFIG_FILE = 'config.ini'
OUTPUT_HEADLINESDATA_FILE = 'Output/Headlines_data.csv'


def get_base_urls_from_config(config_file_path, section_name):
    '''returns a list of base urls for source websites: 
    order in list: vz, lrt, postimees... TO BE UPDATED'''
    base_url_config = ConfigParser()
    base_url_config.read(config_file_path)
    base_urls_config = base_url_config.items(section_name)
    base_urls = []
    for _, b_url in base_urls_config:
        print(f'Found this in config.ini: {b_url}. Adding it to list.')
        base_urls.append(b_url)
    return base_urls

def get_desired_langs(config_file_path, section_name):
    '''returns a list of target languages'''
    lang_config = ConfigParser()
    lang_config.read(config_file_path)
    langs_config = lang_config.items(section_name)
    desired_langs = []
    for _, lang in langs_config:
        desired_langs.append(lang)
    return desired_langs

def main():
    base_urls = get_base_urls_from_config(CONFIG_FILE, 'BASE_URLS')
    desired_langs = get_desired_langs(CONFIG_FILE, 'LANGUAGES')
        
    raw_scrappers_output = []

    # Scrape and output results into raw_scrappers_output list for each website
    vz_scrapper_inst = VzScrapper(base_urls[0], CONFIG_FILE)
    vz_headlines_list = vz_scrapper_inst.get_website_headlines_as_list()
    raw_scrappers_output.append(vz_headlines_list)

    lrt_scrapper_inst = LrtScrapper(base_urls[1], CONFIG_FILE)
    lrt_headlines_list = lrt_scrapper_inst.get_website_headlines_as_list()
    raw_scrappers_output.append(lrt_headlines_list)

    err_scrapper_inst = ERRScrapper(base_urls[2], CONFIG_FILE)
    err_headlines_list = err_scrapper_inst.get_website_headlines_as_list()
    raw_scrappers_output.append(err_headlines_list)

    postimees_scrapper_inst = PostimeesScrapper(base_urls[3], CONFIG_FILE)
    postimees_headlines_list = postimees_scrapper_inst.get_website_headlines_as_list()
    raw_scrappers_output.append(postimees_headlines_list)
    
    btimes_scrapper_inst = BalticTimesScrapper(base_urls[4], CONFIG_FILE)
    btimes_headlines_list = btimes_scrapper_inst.get_website_headlines_as_list()
    raw_scrappers_output.append(btimes_headlines_list)

    db_scrapper_inst = DbScrapper(base_urls[5], CONFIG_FILE)
    db_headlines_list = db_scrapper_inst.get_website_headlines_as_list()
    raw_scrappers_output.append(db_headlines_list)

    print('------COMPLETED SCRAPPING DATA TO LISTS, TRANSLATING, WRITING TO FILE START------')

    for scrapped_list in raw_scrappers_output:
        translator = TranslateList(scrapped_list, desired_langs)
        try:
            translated_headlines_data = translator.get_translated()
            db_scrapper_inst.export_list_to_csv(translated_headlines_data, OUTPUT_HEADLINESDATA_FILE)
        except:
            continue
    print('FINISHED')

if __name__ == '__main__':
    main()