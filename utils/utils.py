from random import choice
from re import findall
import proxyscrape
import requests
import logging
import chardet
import json
import csv
import os


# Objects & Variables Initialization
logger = logging.getLogger(__name__)
COLLECTOR = proxyscrape.create_collector(name='root_collector', resource_types=['http', 'https'], resources='anonymous-proxy')
TEST_IP_URL = 'https://www.httpbin.org/ip'


######### FUNCTION FOR PICKING RANDOM USER AGENT FOR REQUESTS #########

def get_user_agent_dict(user_agents_list):
    '''returns ready to use dict in requests'''
    picked_agent = choice(user_agents_list)
    return {'User-Agent':picked_agent}

def get_user_agent_str(user_agents_list):
    '''returns ready to use str in requests'''
    return choice(user_agents_list)


######### FUNCTIONS FOR ACTIONS WITH CSV FILES #########

def write_or_append_output(output_file):
    '''Check if output file exists and return according option for with-open context manager'''
    if os.path.exists(output_file):
        return 'a'
    else:
        return 'w'

def export_list_to_csv(output_data, output_file, csv_delimiter = '\t'):
    '''write list contents to csv file. Default delimiter: tab'''
    w_a_option = write_or_append_output(output_file)
    with open(output_file, w_a_option, newline='', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter=csv_delimiter)
        for headline_info in output_data:
            csv_writer.writerow(headline_info)

def get_encoding_via_lib(csvfile_path):
    '''gets inside csv encoding'''
    with open(csvfile_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def get_encoding(csvfile_path):
    with open(csvfile_path) as f:
        raw_result = str(f)
    try:
        matches = findall(r"encoding='.+'>", raw_result)
        encoding = matches[0].replace('encoding=\'', '').replace('\'>','')
        return encoding 
    except:
        return get_encoding_via_lib(csvfile_path)

def get_headline_urls_in_db(csvfile_path):
    '''returns list of urls in 'csv database' of already sent headlines'''
    encoding = get_encoding(csvfile_path)
    with open(csvfile_path, 'r', encoding=encoding) as csvfile:
        csv_data = csv.reader(csvfile, delimiter='\t')
        urls_in_db = [headline_data[1] for headline_data in csv_data]
    return urls_in_db

def get_headlines_not_in_db(headlines_data_list, db_urls):
    '''returns a list of headlines data, that are NOT yet in db_urls list. Args:
    headlines_data_list example: [[headline1, url1], [headline2, url2], ...]
    db_urls example: [url1, url2, ...]'''
    new_headline_data = [headline_data for headline_data in headlines_data_list if headline_data[1] not in db_urls]
    return new_headline_data

def csv_contents_to_list(csvfile_path):
    '''reads csv data with default tab delimiter and returns a list'''
    with open(csvfile_path, 'r', encoding='utf-8') as csvfile:
        csv_data = csv.reader(csvfile, delimiter='\t')
        csv_headline_data = [headline_data for headline_data in csv_data]
    return csv_headline_data


######### FUNCTIONS FOR GETTING WORKING PROXY #########

def get_proxy_dict_identities():
    '''uses initialized collector object from proxyscrape to return proxies dict'''
    # http_type = https_or_http(target_url)
    raw_proxy_https_data = COLLECTOR.get_proxy({'type':'https', 'code':('us', 'uk', 'de', 'fr', 'ca', 'se', 'no'),'anonymous':True})
    raw_proxy_http_data = COLLECTOR.get_proxy({'type':'http', 'code':('us', 'uk', 'de', 'fr', 'ca', 'se', 'no'),'anonymous':True})
    # Constructing sockets:    
    logger.debug(f'New https proxy: {raw_proxy_https_data}; New http proxy: {raw_proxy_http_data}')
    http_proxy_socket = f'{raw_proxy_http_data[0]}:{raw_proxy_http_data[1]}' 
    https_proxy_socket = f'{raw_proxy_https_data[0]}:{raw_proxy_https_data[1]}' 
    proxies_dict = {'https':https_proxy_socket, 'http':http_proxy_socket}
    return proxies_dict

def get_ip(proxy=None):
    '''returns original (no proxy) ip by default; returns proxy ip if proxy was passed'''
    r = requests.get(TEST_IP_URL, proxies=proxy, timeout=5)
    data = json.loads(r.text)
    client_ip = data['origin']
    logger.info(f'{TEST_IP_URL} returning IP: {client_ip}')
    return client_ip

def get_working_proxy(max_attempts=30):
    '''(HTTPS ONLY!) gets, tests, returns working proxy. If fails max_attempts times, returns None.'''
    client_ip = get_ip()
    proxies = get_proxy_dict_identities()
    attempt = 0
    while True:
        try: 
            attempt += 1
            logger.info(f'Testing {proxies} picked proxies. Attempt: {attempt}') 
            if attempt == max_attempts:
                logger.error(f'Maximum number of {max_attempts} attempts has been reached. Goes we will go without a proxy this time...')
                return None
            changed_ip = get_ip(proxies)
            if changed_ip != client_ip:
                logger.info(f'Found working https proxy: {proxies}!')
                return proxies
        except:
            logger.error(f'Failed to pick working proxy. No of attempts remaining: {max_attempts-attempt}. Getting a new set of proxies')
            proxies = get_proxy_dict_identities()
            continue


if __name__ == '__main__':
    pass