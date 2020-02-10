from scrappers import VzScrapper, LrtScrapper, ERRScrapper, PostimeesScrapper, BalticTimesScrapper, DbScrapper
from translate import TranslateList
from configparser import ConfigParser
from datetime import datetime
import logging
import logging.handlers
import csv

# LOGGING CONFIG:
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('\n%(levelname)s:%(module)s: %(message)s :%(funcName)s')
file_handler = logging.handlers.RotatingFileHandler('newsletter.log', maxBytes=10000, backupCount=3)
file_handler.setFormatter(formatter)

# Additional Console logging
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARNING)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# GLOBAL VARIABLES:
CONFIG_FILE = 'config.ini'
OUTPUT_HEADLINES_FILE = 'Output/Headlines_data.csv'
FORMATTED_TIMESTAMP = datetime.today().strftime(r'%Y.%m.%d %H.%M')
OUTPUT_SENT_TODAY_FILE = f'Output/Headlines_sent {FORMATTED_TIMESTAMP}.csv'
SCRAPPERS = [VzScrapper, LrtScrapper, ERRScrapper, PostimeesScrapper, BalticTimesScrapper, DbScrapper]


def get_config_section_values(config_file_path, section_name):
    '''returns section in config file values as list'''
    config = ConfigParser()
    config.read(config_file_path)
    config_section_data = config.items(section_name)
    return [value for _, value in config_section_data]

def get_headline_urls_in_db(csvfile_path):
    '''returns list of urls in 'csv database' of already sent headlines'''
    with open(csvfile_path, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter='\t')
        urls_in_db = [headline_data[1] for headline_data in csv_data]
    logger.info(f'Collected {len(urls_in_db)} headlines in database.')
    return urls_in_db

def reduce_raw_list(headlines_data_list, db_urls):
    '''returns a list of headlines data, that are NOT yet in db_urls list'''
    new_headline_data = [headline_data for headline_data in headlines_data_list if headline_data[1] not in db_urls]
    return new_headline_data

def scrape_websites_headlines_to_list(base_urls, scrappers_list):
    '''returns a list of website specific lists of lists headline data. Args: 
    base_urls - list of website base url addresses from config file
    scrappers_list - list of scrapper classes'''
    raw_scrappers_output = []
    for idx, ScrapperClass in enumerate(scrappers_list):
        try:
            scrapper_inst = ScrapperClass(base_urls[idx], CONFIG_FILE)
            headlines_data = scrapper_inst.get_website_headlines_as_list()
            raw_scrappers_output.append(headlines_data)
        except:
            logger.error(f'Error occured while scrapping {base_urls[idx]} in {ScrapperClass}, proceeding to next website...')
            continue
    return raw_scrappers_output

def main():
    logger.info(f'------------------------------------FRESH START ON {FORMATTED_TIMESTAMP}------------------------------------')
    base_urls = get_config_section_values(CONFIG_FILE, 'BASE_URLS')
    desired_langs = get_config_section_values(CONFIG_FILE, 'LANGUAGES')
    urls_in_db = get_headline_urls_in_db(OUTPUT_HEADLINES_FILE) 

    # Scrape and output results into raw_scrappers_output list for each website
    raw_scrappers_output = scrape_websites_headlines_to_list(base_urls, SCRAPPERS)

    logger.info('------COMPLETED SCRAPPING DATA TO LISTS, TRANSLATING, WRITING TO FILE START------')
    # Instance to use export to csv method inside a class:
    db_scrapper_inst = DbScrapper(base_urls[5], CONFIG_FILE)

    headlines_to_email = []
    for idx, scrapped_list in enumerate(raw_scrappers_output):
        # Export separate, untranslated, raw scrape output from each website as separate csv (temporary)        
        db_scrapper_inst.export_list_to_csv(scrapped_list, 'Output/Headlines_data('+ str(idx) +').csv')
        # Compare to "csv db" entries and reduce load working with new headlines only before passing for language processing
        scrapped_new_list = reduce_raw_list(scrapped_list, urls_in_db)
        logger.debug(f'New headlines for {base_urls[idx]} being passed to TranslateList: {len(scrapped_new_list)}')
        if scrapped_new_list:    
            translator = TranslateList(scrapped_new_list, desired_langs)
            try:
                translated_headlines_data = translator.get_translated()
                headlines_to_email = headlines_to_email + translated_headlines_data
            except:
                logger.warning(f'Failed to translate {idx} member in headlines list containing stripped {len(scrapped_new_list)} new headlines. Moving on...')
                continue
        else:
            logger.warning('All scrapped headlines are already in csv database. Consider running script later')
    
    # Send email with new headlines in 'headlines_to_email' list:
    # To be added...

    # Export translated, new headlines in separate csv:
    db_scrapper_inst.export_list_to_csv(headlines_to_email, OUTPUT_SENT_TODAY_FILE)
    
    # Writing headlines to db:
    db_scrapper_inst.export_list_to_csv(headlines_to_email, OUTPUT_HEADLINES_FILE)
    
    logger.info(f'------------------------------------FINISHED------------------------------------')

if __name__ == '__main__':
    main()