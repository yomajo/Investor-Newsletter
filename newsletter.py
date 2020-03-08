from scrappers import VzScrapper, LrtScrapper, ERRScrapper, PostimeesScrapper, BalticTimesScrapper, DbScrapper
from utils import EmailHandler, export_list_to_csv, get_headline_urls_in_db, get_headlines_not_in_db
from configparser import ConfigParser
from translate import TranslateList
from datetime import datetime
import logging.handlers
import logging

# LOGGING CONFIG:
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('\n%(levelname)s:%(module)s: %(message)s :%(funcName)s')
file_handler = logging.handlers.RotatingFileHandler('newsletter.log', maxBytes=10**6, backupCount=3)
file_handler.setFormatter(formatter)

# Additional Console logging
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

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
            logger.exception(f'Error occured while scrapping {base_urls[idx]} in {ScrapperClass.__name__}, proceeding to next website...')
            continue
    return raw_scrappers_output

def main():
    logger.info(f'------------------------------------FRESH START ON {FORMATTED_TIMESTAMP}------------------------------------')
    base_urls = get_config_section_values(CONFIG_FILE, 'BASE_URLS')
    desired_langs = get_config_section_values(CONFIG_FILE, 'LANGUAGES')
    urls_in_db = get_headline_urls_in_db(OUTPUT_HEADLINES_FILE) 

    # Scrape and output results into raw_scrappers_output list for each website
    raw_scrappers_output = scrape_websites_headlines_to_list(base_urls, SCRAPPERS)

    logger.info('------COMPLETED SCRAPPING DATA TO LISTS, TRANSLATING')

    headlines_to_email = []
    for idx, scrapped_list in enumerate(raw_scrappers_output):
        # Export separate, untranslated, raw scrape output from each website as separate csv (temporary)        
        logger.debug(f'Exporting raw data ({len(scrapped_list)} headlines) from {base_urls[idx]} to Output/Headlines_data({idx}).csv')
        export_list_to_csv(scrapped_list, 'Output/Headlines_data(' + str(idx) +').csv')
        # Compare to "csv db" entries and reduce load working with new headlines only before passing for language processing
        scrapped_new_headlines = get_headlines_not_in_db(scrapped_list, urls_in_db)
        logger.info(f'Scrapped {len(scrapped_list)} headlines from {base_urls[idx]}. New headlines found: {len(scrapped_new_headlines)}')
        logger.debug(f'{len(scrapped_new_headlines)} new headlines from ---{base_urls[idx]}--- being passed to TranslateList')
        if scrapped_new_headlines:    
            translator = TranslateList(scrapped_new_headlines, desired_langs)
            try:
                translated_headlines_data = translator.get_translated()
                logger.info(f'{len(translated_headlines_data)} headlines from {base_urls[idx]} have been successfully translated and added to headlines_to_email list')
                headlines_to_email += translated_headlines_data
            except:
                logger.exception(f'Failed to translate headlines from {base_urls[idx]} containing stripped {len(scrapped_new_headlines)} new headlines. Moving on...')
                continue
        else:
            logger.warning('All scrapped headlines are already in csv database. Consider running script later')

    logger.info('------Translation finished. Exporting data, saving to database, sending emails...')
    
    # Send email with new headlines in 'headlines_to_email' list:
    send_email(headlines_to_email)
    
    # Export translated, new headlines in separate csv:
    export_list_to_csv(headlines_to_email, OUTPUT_SENT_TODAY_FILE)
    
    # Writing headlines to db:
    export_list_to_csv(headlines_to_email, OUTPUT_HEADLINES_FILE)
    
    logger.info(f'------------------------------------FINISHED------------------------------------')

headlines_list_of_lists = [
    ['Chill Vibe Old School Trance', 'https://www.youtube.com/watch?v=VTGVxcRt8OI'],
    ['Sample Blog', 'http://www.sampleblog.com'],
    ['Python documentation on emails', 'https://docs.python.org/3/library/email.message.html']
    ]

def output_template(headlines_list_of_lists):
    email_client = EmailHandler(headlines_list=headlines_list_of_lists)
    email_client.test_output_rendered_html()

def send_email(headlines_list_of_lists):
    email_client = EmailHandler(headlines_list=headlines_list_of_lists)
    email_client.run()

if __name__ == '__main__':
    # print('You are about to receive an email hopefully')
    # output_template(headlines_list_of_lists)
    # send_email(headlines_list_of_lists)
    # print('Aaaand, its time to test shit.')
    main()