from random import choice, randint
from bs4 import BeautifulSoup
from time import sleep
import requests
import logging
import json
import csv
import os


# Objects & Variables Initialization
logger = logging.getLogger(__name__)
TEST_IP_URL = 'https://www.httpbin.org/ip'
PROXY_SOURCE_URL = 'https://free-proxy-list.net/anonymous-proxy.html'
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
    with open(output_file, w_a_option, newline='') as f:
        csv_writer = csv.writer(f, delimiter=csv_delimiter)
        for headline_info in output_data:
            csv_writer.writerow(headline_info)

def get_headline_urls_in_db(csvfile_path):
    '''returns list of urls in 'csv database' of already sent headlines. If no file - return empty list'''
    if os.path.exists(csvfile_path):
        with open(csvfile_path, 'r') as csvfile:
            csv_data = csv.reader(csvfile, delimiter='\t')
            urls_in_db = []
            for headline_data in csv_data:
                try:
                    urls_in_db.append(headline_data[1])
                except:
                    logging.exception(f'Could not decode {headline_data}, skipping line...')
                    continue
            # urls_in_db = [headline_data[1] for headline_data in csv_data]
        return urls_in_db
    return []

def get_headlines_not_in_db(headlines_data_list, db_urls):
    '''returns a list of headlines data, that are NOT yet in db_urls list. Args:
    headlines_data_list example: [[headline1, url1], [headline2, url2], ...]
    db_urls example: [url1, url2, ...]'''
    new_headline_data = [headline_data for headline_data in headlines_data_list if headline_data[1] not in db_urls]
    return new_headline_data

def csv_contents_to_list(csvfile_path):
    '''reads csv data with default tab delimiter and returns a list'''
    with open(csvfile_path, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter='\t')
        csv_headline_data = [headline_data for headline_data in csv_data]
    return csv_headline_data


######### FUNCTIONS FOR GETTING WORKING PROXY #########

def get_proxy_from_td_elems(td_elements):
    '''returns host:ip from passed BSoup object td_elements'''
    host = td_elements[0].text
    port = td_elements[1].text
    return f'{host}:{port}'

def get_proxies_tbody():
    '''gets html soup with proxies data in it'''
    try:
        r = requests.get(PROXY_SOURCE_URL, timeout=10)
        soup = BeautifulSoup(r.text, features='lxml')
        try:
            return soup.tbody
        except:
            logger.exception(f'Proxy Source website {PROXY_SOURCE_URL} changed structure dramatically. No tbody in HTML found.')
            return None
    except:
        logger.exception(f'Proxy Source website {PROXY_SOURCE_URL} seems to be down, unable to get response')
        return None

def get_sockets_lists():
    '''returns lists of https and http proxies'''
    try:
        proxies_table = get_proxies_tbody()
        t_rows = proxies_table.findAll('tr')
        https_proxies = []
        http_proxies = []
        for t_row in t_rows:
            td_elements = t_row.findAll('td')
            # collecting https/http sockets:
            if td_elements[6].text == 'yes':
                proxy = get_proxy_from_td_elems(td_elements)
                https_proxies.append(proxy)
            else:
                proxy = get_proxy_from_td_elems(td_elements)
                http_proxies.append(proxy)
        logger.info(f'Finished collecting proxies. https list has {len(https_proxies)} members. http: {len(http_proxies)}')
        return https_proxies, http_proxies
    except:
        logger.exception(f'Proxy source website {PROXY_SOURCE_URL} structure changed. Problems scrapping table rows')
        return None, None

def get_ip(client_socket='1.1.1.1', proxy=None):
    '''returns original (no proxy) ip by default; returns proxy ip if proxy was passed'''
    try:
        r = requests.get(TEST_IP_URL, proxies=proxy, timeout=10)
        data = json.loads(r.text)
        client_ip = data['origin']
        # print((f'{TEST_IP_URL} returning IP: {client_ip}'))
        logger.info(f'{TEST_IP_URL} returning IP: {client_ip}')
        sleep(3/randint(1,10))
        return client_ip
    except:
        logger.exception(f'Error occured while trying to retrieve IP address. {TEST_IP_URL} website down/blocked?, returning client_socket: {client_socket}')
        return client_socket

def get_working_proxy():
    '''(HTTPS ONLY!) gets, tests, returns working proxy. If fails max_attempts times, returns None.'''
    try:
        client_ip = get_ip()
        # If test website is down, prevent from returning default client ip:
        if client_ip == '1.1.1.1':
            logger.error(f'Seems {TEST_IP_URL} website is down. Unable to test any of proxies, returning None')
            return None
        https_sockets, http_sockets = get_sockets_lists()
        max_attempts = len(max([https_sockets, http_sockets], key=len))
    except:
        logger.exception(f'Could not get client or return sockets lists. Returning working proxy: None')
        return None

    attempt = 0
    while True:
        try: 
            attempt += 1
            picked_https_socket = choice(https_sockets)
            picked_http_socket = choice(http_sockets)
            proxies = {'https': picked_https_socket, 'http': picked_http_socket}
            # print((f'Testing {proxies} picked proxies. Attempt: {attempt}') )
            logger.info(f'Testing {proxies} picked proxies. Attempt: {attempt}') 
            changed_ip = get_ip(client_ip, proxies)
            if changed_ip == None:
                return None
            if changed_ip != client_ip:
                # print(f'Found working https proxy: {proxies}!')
                logger.info(f'Found working https proxy: {proxies}!')
                return proxies
            if attempt == max_attempts:
                # print(f'Maximum number of {max_attempts} attempts has been reached. Goes we will go without a proxy this time...')
                logger.error(f'Maximum number of {max_attempts} attempts has been reached. Goes we will go without a proxy this time...')
                return None
        except:
            logger.error(f'Failed to pick working proxy. No of attempts remaining: {max_attempts-attempt}. Blacklisting selection, getting a new set of proxies')
            https_sockets.remove(picked_https_socket)
            http_sockets.remove(picked_http_socket)
            continue


if __name__ == '__main__':
    pass
    # proxies = get_working_proxy()
    # print(proxies)