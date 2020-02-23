from utils import get_user_agent_str, get_working_proxy, USER_AGENTS
from googletrans import Translator, LANGUAGES
from time import sleep
import langdetect
import logging

# Initializing logging in module
logger = logging.getLogger(__name__)

class TranslateList():
    '''Based on googletrans Translator, tailored for project needs. Works on uniform language list only. Takes args:
    - src_list - scrapped results (list of lists), where first member of each list is string headline sentence
    - desired_lang_list - list of desired output languages (target lang is first member in list)'''

    def __init__(self, src_list, desired_lang_list):
        self.src_list = src_list
        self.desired_lang_list = desired_lang_list
        self.expected_langs = ['en', 'et', 'lv', 'lt']
        self.detection_confidence = 0.9
        self.sleep_time = 100
    
    def init_translator(self):
        '''get user agent, proxies & initialize Translator instance'''
        user_agent = get_user_agent_str(USER_AGENTS)
        proxies = get_working_proxy()
        logger.debug(f'While initializing Translate() class going with proxies: {proxies}')
        self.translator = Translator(user_agent=user_agent, proxies=proxies, timeout=30)

    def desired_langs_supported(self):
        '''check if desired languages are supported by googletrans package'''
        for lang in self.desired_lang_list:
            if lang not in LANGUAGES:
                logger.exception(f'Passed target language for TranslateList class {lang} is not supported by googletrans library')
                raise Exception
        return True

    def strip_src_to_headings(self):
        '''returns a flat list of headlines extracted from list of lists'''
        headings = []
        for headline_data in self.src_list:
            headings.append(headline_data[0])
        return headings

    def get_headlines_list_lang(self, raw_headlines_list):
        '''traverses all list members; deletes members below language detection confidence or not of expected lang list, returns detected lang. Detection via langdetect'''
        detected_langs = []
        for idx, headline in enumerate(raw_headlines_list):
            top_detect_res = langdetect.detect_langs(headline)[0]
            lang, confidence = top_detect_res.lang, top_detect_res.prob
            if lang not in self.expected_langs or confidence < self.detection_confidence:
                logger.warning(f'Unexpected language or confidence level too low in member found at index {idx}, detect_obj: {top_detect_res}, content: {headline}. Deleting member')
                self.delete_member(idx)
                continue
            if lang not in detected_langs:
                detected_langs.append(lang)
        if len(detected_langs) != 1:
            logger.warning(f'Passed list contains more than one language. Detected languages contain: {detected_langs}')
            raise Exception(f'Not processing this list. Language detection results: {detected_langs}')
        return detected_langs[0]

    def delete_member(self, idx):
        '''removes member at idx from self.src_list passed to cls and stripped self.headings'''
        self.headlines.pop(idx)
        self.src_list.pop(idx)

    def get_translation_obj(self, list_to_translate, src_lang, trg_lang, max_attempts=10):
        '''Attempts max_attempts times to initialize Translator cls with working proxy;
        returns iterable translation object querying google translate if everything goes fine'''
        attempt = 0
        while True:
            try:
                attempt += 1
                # Terminate loop and whole translation class stuff returning None if could not work things out in max_attempts
                if attempt == max_attempts:
                    logger.error(f'Maximum number of {max_attempts} attempts has been reached. Could not find working Translator and Proxy pair')
                    return None
                self.init_translator()
                logger.debug('---Before requesting google API---')
                translation_objs = self.translator.translate(list_to_translate, src=src_lang ,dest=trg_lang)
                logger.debug('---After requesting google API---')
                return translation_objs
            except:
                logger.warning(f'Attempt {attempt} failed in creating Translator object create lang translation objects. Trying again...')
                continue

    def bulk_translate(self, list_to_translate, src_lang, trg_lang):
        '''translate passed list from src_lang to trg_lang'''
        translated_headlines = []
        try:
            translator_objs = self.get_translation_obj(list_to_translate, src_lang, trg_lang)
            for idx, translation in enumerate(translator_objs):
                translated_headlines.append(translation.text)
                logger.debug(f'Progress: {idx+1}/{len(translator_objs)} headlines; translated headline: {translation.text}')
            return translated_headlines
        except:
            logger.exception(f'Error occured while iterating translation object at: {translation} among {len(translator_objs)} members')
            raise Exception

    def lists_same_length(self, src_list, translated_list):
        '''simply compared lengths of passed lists'''
        return len(src_list) == len(translated_list)

    def construct_src_size_output(self, src_list, translated_list):
        '''returns src_list size/form list with headlines replaced from passed translated_list'''
        if self.lists_same_length(src_list, translated_list):
            output_translated_list = self.src_list
            for idx, headline_data in enumerate(output_translated_list):
                headline_data[0] = translated_list[idx]
            return output_translated_list
        else:
            logger.exception(f'Could not map lists while constructing output. translated_list len: {len(translated_list)} while src_list len: {len(self.src_list)}')
            raise Exception

    def get_total_chars(self, list_to_calc):
        '''prints out total characters passed to be proccessed to google translate'''
        chars = 0
        for item in list_to_calc:
            chars += len(item)
        logger.info(f'Calculated total number characters in passed headlines list is {chars}')

    def get_translated(self):
        '''if possible, returns translated list'''        
        if self.desired_langs_supported():
            self.headlines = self.strip_src_to_headings()
            self.get_total_chars(self.headlines)
            logger.info(f'Detecting headlines list language consistency and original language')
            detected_src_lang = self.get_headlines_list_lang(self.headlines)
            # Translate only if detected language is not in target langs list passed as desired_lang_list
            if detected_src_lang not in self.desired_lang_list:    
                logger.info(f'Detected language in passed list: {detected_src_lang}, translating...')
                translated_headlines = self.bulk_translate(self.headlines, detected_src_lang, self.desired_lang_list[0])
                translated_cls_output = self.construct_src_size_output(self.src_list, translated_headlines)
                logging.debug('Outputing translated output')
                return translated_cls_output
            else:
                logger.info(f'Returning without translation. Detected lang \'{detected_src_lang}\' already in {self.desired_lang_list}')
                return self.src_list


if __name__ == '__main__':
    pass