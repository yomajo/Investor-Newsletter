import os
import csv


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

def get_headline_urls_in_db(csvfile_path):
    '''returns list of urls in 'csv database' of already sent headlines'''
    with open(csvfile_path, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter='\t')
        urls_in_db = [headline_data[1] for headline_data in csv_data]
    return urls_in_db

def get_headlines_not_in_db(headlines_data_list, db_urls):
    '''returns a list of headlines data, that are NOT yet in db_urls list. Args:
    headlines_data_list example: [[headline1, url1], [headline2, url2], ...]
    db_urls example: [url1, url2, ...]'''
    new_headline_data = [headline_data for headline_data in headlines_data_list if headline_data[1] not in db_urls]
    return new_headline_data


if __name__ == '__main__':
    pass