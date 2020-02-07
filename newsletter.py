from scrappers import VzScrapper, LrtScrapper, ERRScrapper, PostimeesScrapper, BalticTimesScrapper, DbScrapper
from translate import TranslateList
from configparser import ConfigParser
import csv

# GLOBAL VARIABLES:
CONFIG_FILE = 'config.ini'
OUTPUT_HEADLINES_FILE = 'Output/Headlines_data.csv'


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

def get_headline_urls_in_db(csvfile_path):
    '''returns list of urls in 'csv database' of already sent headlines'''
    with open(csvfile_path, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter='\t')
        urls_in_db = [headline_data[1] for headline_data in csv_data]
    print(f'Collected {len(urls_in_db)} headlines in database.')
    return urls_in_db

def reduce_raw_list(headlines_data_list, db_urls):
    '''returns a list of headlines data, that are NOT yet in db_urls list'''
    new_headline_data = [headline_data for headline_data in headlines_data_list if headline_data[1] not in db_urls]
    return new_headline_data


def main():
    base_urls = get_base_urls_from_config(CONFIG_FILE, 'BASE_URLS')
    desired_langs = get_desired_langs(CONFIG_FILE, 'LANGUAGES')
    urls_in_db = get_headline_urls_in_db(OUTPUT_HEADLINES_FILE) 
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

    for idx, scrapped_list in enumerate(raw_scrappers_output):
        # Export separate, untranslated, raw scrape output from each website as separate csv (temporary)
        db_scrapper_inst.export_list_to_csv(scrapped_list, 'Output/Headlines_data('+ str(idx) +').csv')
        # Compare to "csv db" entries and reduce load working with new headlines only before passing for language processing
        scrapped_new_list = reduce_raw_list(scrapped_list, urls_in_db)
        print(f'New headlines for {base_urls[idx]} being passed to TranslateList: {len(scrapped_new_list)}')
        headlines_to_email = []
        if scrapped_new_list:    
            translator = TranslateList(scrapped_new_list, desired_langs)
            try:
                translated_headlines_data = translator.get_translated()
                headlines_to_email = headlines_to_email + translated_headlines_data
            except:
                print(f'Failed to translate {idx} headlines list containing stripped {len(scrapped_new_list)} new headlines. Moving on...')
                continue
        else:
            print('All scrapped headlines are already in csv database. Consider running script later')
    
    # Send email with new headlines in 'headlines_to_email' list:
    # To be added...
    
    # Writing headlines to db:
    db_scrapper_inst.export_list_to_csv(headlines_to_email, OUTPUT_HEADLINES_FILE)
    
    print('\nFINISHED')


if __name__ == '__main__':
    main()