from scrappers.vz_scrapper import VzScrapper
from scrappers.lrt_scrapper import LrtScrapper
from scrappers.err_scrapper import ERRScrapper
from scrappers.postimees_scrapper import PostimeesScrapper
from scrappers.baltictimes_scrapper import BalticTimesScrapper
from scrappers.db_scrapper import DbScrapper
from translate import TranslateList
from configparser import ConfigParser

# GLOBAL VARIABLES:
config_file = 'config.ini'


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
    base_urls = get_base_urls_from_config(config_file, 'BASE_URLS')
    # base_url_vz = base_urls[0]
    base_url_lrt = base_urls[1]
    # base_url_err = base_urls[2]
    # base_url_postimees = base_urls[3]
    # base_url_btimes = base_urls[4]
    # base_url_db = base_urls[5]

    desired_langs = get_desired_langs(config_file, 'LANGUAGES')
    print(desired_langs)
    # vz_scrapper_inst = VzScrapper(base_url_vz, config_file, 'Output/vz_headlines.csv')
    # vz_headlines_list = vz_scrapper_inst.get_website_headlines_as_list()
    # vz_scrapper_inst.export_list_to_csv(vz_headlines_list, vz_scrapper_inst.output_csv_file)
    # lrt_scrapper_inst = LrtScrapper(base_url_lrt, config_file, 'Output/lrt_headlines.csv')
    # lrt_headlines_list = lrt_scrapper_inst.get_website_headlines_as_list()
    # lrt_scrapper_inst.export_list_to_csv(lrt_headlines_list, lrt_scrapper_inst.output_csv_file)
    # err_scrapper_inst = ERRScrapper(base_url_err, config_file, 'Output/err_headlines(no translaation yet).csv')
    # err_headlines_list = err_scrapper_inst.get_website_headlines_as_list()
    # err_scrapper_inst.export_list_to_csv(err_headlines_list, err_scrapper_inst.output_csv_file)
    # postimees_scrapper_inst = PostimeesScrapper(base_url_postimees, config_file, 'Output/postimees_headlines(no translaation yet).csv')
    # postimees_headlines_list = postimees_scrapper_inst.get_website_headlines_as_list()
    # postimees_scrapper_inst.export_list_to_csv(postimees_headlines_list, postimees_scrapper_inst.output_csv_file)
    # btimes_scrapper_inst = BalticTimesScrapper(base_url_btimes, config_file, 'Output/baltic_times_headlines.csv')
    # btimes_headlines_list = btimes_scrapper_inst.get_website_headlines_as_list()
    # btimes_scrapper_inst.export_list_to_csv(btimes_headlines_list, btimes_scrapper_inst.output_csv_file)
    # db_scrapper_inst = DbScrapper(base_url_db, config_file, 'Output/db_headlines.csv')
    # db_headlines_list = db_scrapper_inst.get_website_headlines_as_list()
    # db_scrapper_inst.export_list_to_csv(db_headlines_list, db_scrapper_inst.output_csv_file)



if __name__ == '__main__':
    main()