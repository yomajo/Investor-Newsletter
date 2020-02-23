from utils import get_user_agent_str, get_working_proxy, USER_AGENTS
from googletrans import Translator, LANGUAGES
from time import sleep
import langdetect
import logging
from pprint import pprint

# Initializing logging in module
logger = logging.getLogger(__name__)

# Harddcoded test_list
test_headline_data = [['Atšaukta didžiausia pasaulyje telekomunikacijų paroda',
        'https://www.vz.lt/technologijos-mokslas/2020/02/12/atsaukta-didziausia-pasaulyje-telekomunikaciju-paroda'],
        ['Mato prielaidų šiemet atpigti vairuotojų privalomajam draudimui',
        'https://www.vz.lt/finansai-apskaita/bankai-draudimas/2020/02/14/mato-prielaidu-siemet-atpigti-vairuotoju-privalomajam-draudimui'],
        ['Kaip patikrinti, ką darbuotojai išmoko mokymuose',
        'https://www.vz.lt/smulkusis-verslas/2020/02/13/kaip-patikrinti-ka-darbuotojai-ismoko-mokymuose'],
        ['Atšaukta didžiausia pasaulyje telekomunikacijų paroda',
        'https://www.vz.lt/technologijos-mokslas/2020/02/12/atsaukta-didziausia-pasaulyje-telekomunikaciju-paroda'],
        ['Iškreipta realybė: Graikijos ir Italijos obligacijos graibstomos kaip '
        'saugumo užuovėja',
        'https://www.vz.lt/rinkos/2020/02/18/iskreipta-realybe-graikijos-ir-italijos-obligacijos-graibstomos-kaip-saugumo-uzuoveja'],
        ['Lumenappus sunnib suusakeskuseid lume hankimiseks äärmuslikke viise otsima',
        'https://www.err.ee/1036324/lumenappus-sunnib-suusakeskuseid-lume-hankimiseks-aarmuslikke-viise-otsima'],
        ['Soe talv, suvised hinnad: ületootmine ajas maagaasi hinna rekordmadalale',
        'https://www.err.ee/1036195/soe-talv-suvised-hinnad-uletootmine-ajas-maagaasi-hinna-rekordmadalale'],
        ['Triin Kutberg: alkoholiaktsiisi langetamine mõjus majandusele positiivselt',
        'https://www.err.ee/1054639/triin-kutberg-alkoholiaktsiisi-langetamine-mojus-majandusele-positiivselt'],
        ['Uus Läti-Eesti elektriliin võib tulla Liivi merepargi kaudu',
        'https://www.err.ee/1036888/uus-lati-eesti-elektriliin-voib-tulla-liivi-merepargi-kaudu'],
        ['Eesti koos veel kaheksa riigiga kaalub EL-i maanteepaketi tõttu kohtuteed',
        'https://www.err.ee/1036795/eesti-koos-veel-kaheksa-riigiga-kaalub-el-i-maanteepaketi-tottu-kohtuteed'],
        ["Belarus orders two more oil tankers via Lithuania's Klaipeda",
        'https://www.baltictimes.com/belarus_orders_two_more_oil_tankers_via_lithuania_s_klaipeda/'],
        ["Belarus orders two more oil tankers via Lithuania's Klaipeda",
        'https://www.baltictimes.com/belarus_orders_two_more_oil_tankers_via_lithuania_s_klaipeda/'],
        ['Utena brewery is the first in the country to eliminate CO 2 emissions: '
        'exclusive status granted',
        'https://www.baltictimes.com/utena_brewery_is_the_first_in_the_country_to_eliminate_co_2_emissions__exclusive_status_granted/'],
        ['Lithuania chosen as a launchpad to EU markets – Cinganta',
        'https://www.baltictimes.com/lithuania_chosen_as_a_launchpad_to_eu_markets___cinganta/'],
        ['Two Latvian citizens convicted of large-scale fraud in the United States',
        'https://www.baltictimes.com/two_latvian_citizens_convicted_of_large-scale_fraud_in_the_united_states/'],
        ['Finanšu tehnoloģiju uzņēmumi nolūko Vjetnamu',
        'https://www.db.lv/zinas/finansu-tehnologiju-uznemumi-noluko-vjetnamu-494934'],
        ['Maksājumu jomā transformācija turpināsies',
        'https://www.db.lv/zinas/maksajumu-joma-transformacija-turpinasies-494760'],
        ['Elektroenerģijas ražotājs AS Residence Energy par labu Meridian Trade Bank '
        'ieķīlājis visu mantu',
        'https://www.db.lv/zinas/elektroenergijas-razotajs-as-residence-energy-par-labu-meridian-trade-bank-iekilajis-visu-mantu-494452'],
        ['Kā top? Ziemeļu Enkurs alus',
        'https://www.db.lv/zinas/ka-top-ziemelu-enkurs-alus-494781'],
        ['Twitter ienākumi pārlec miljardam',
        'https://www.db.lv/zinas/twitter-ienakumi-parlec-miljardam-494804']]

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
        logger.info(f'Returning first detected list language: {detected_langs[0]}, total detected languages in list: {len(detected_langs)}')
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
                translation_objs = self.translator.translate(list_to_translate, src='auto' ,dest=trg_lang)
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
        '''returns True if passed lists contain same length'''
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
    # pass
    translator = TranslateList(test_headline_data, ['en'])
    translated_list = translator.get_translated()
    pprint(translated_list)