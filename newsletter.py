from scrappers.vz_scrapper import VzScrapper
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


def main():
    base_urls = get_base_urls_from_config(config_file, 'BASE_URLS')
    base_url_vz = base_urls[0]

    vz_scrapper_inst = VzScrapper(base_url_vz, config_file, 'Output/vz_headlines.csv')

    vz_headlines_list = vz_scrapper_inst.get_website_headlines_as_list()
    vz_scrapper_inst.export_list_to_csv(vz_headlines_list, vz_scrapper_inst.output_csv_file)


if __name__ == '__main__':
    main()