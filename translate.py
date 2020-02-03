from googletrans import Translator, LANGUAGES
from time import sleep


class TranslateList():
    '''Based on googletrans Translator, tailored for project needs. Works on uniform language list only. Takes args:
    - src_list - scrapped results (list of lists), where first member of each list is string headline sentence
    - desired_lang_list - list of desired output languages (target lang is first member in list)'''

    def __init__(self, src_list, desired_lang_list):
        self.src_list = src_list
        self.desired_lang_list = desired_lang_list
        self.translator = Translator()
        self.expected_langs = ['en', 'et', 'lv', 'lt']
        self.detection_confidence = 0.8
        self.sleep_time = 0.4

    def desired_langs_supported(self):
        '''check if desired languages are supported by googletrans package'''
        for lang in self.desired_lang_list:
            if lang not in LANGUAGES:
                raise Exception(f'Passed target language for TranslateList class {lang} is not supported by googletrans library')
        return True

    def strip_src_to_headings(self):
        '''returns a flat list of headlines extracted from list of lists'''
        headings = []
        for headline_data in self.src_list:
            headings.append(headline_data[0])
        print(f'Formed a stripped list of headlines only. Source list length: {len(self.src_list)}, new list length: {len(headings)}')
        return headings

    def get_headlines_list_lang(self, raw_headlines_list):
        '''traverses all list members; deletes members below language detection confidence or not of expected lang list, returns detected lang'''
        self.get_detected_lang_obj_list(self.headlines)
        detected_langs = []
        for idx, detect_obj in enumerate(self.detected_lang_objs):
            sleep(self.sleep_time)
            print(f'Inside get_headlines_list_lang. Iterating over in {idx} member')
            if detect_obj.lang not in self.expected_langs or detect_obj.confidence < self.detection_confidence:
                print(f'Unexpected language or confidence level too low in member found at index {idx}, detect_obj: {detect_obj}. Deleting member')
                self.delete_member(idx)
                break
            if detect_obj.lang not in detected_langs:
                detected_langs.append(detect_obj.lang)
            continue
        if len(detected_langs) != 1:
            raise Exception(f'Passed list contains more than one language. Detected languages contain: {detected_langs}')
        return detected_langs[0]

    def get_detected_lang_obj_list(self, raw_headlines_list):
        '''gets iterable detection object querying google translate'''
        try:
            sleep(self.sleep_time)
            self.detected_lang_objs = self.translator.detect(raw_headlines_list)
        except:
            raise Exception('Failed to create lang detection objects inside \'get_detected_lang_obj_list\' method')
        

    def delete_member(self, idx):
        '''removes member at idx from self.src_list passed to cls and stripped self.headings'''
        self.headlines.pop(idx)
        self.src_list.pop(idx)

    def bulk_translate(self, list_to_translate, src_lang, trg_lang):
        '''translate passed list from src_lang to trg_lang'''
        translated_headlines = []
        translation_objs = self.translator.translate(list_to_translate, src=src_lang ,dest=trg_lang)
        for translation in translation_objs:
            translated_headlines.append(translation.text)
        return translated_headlines
    
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
            raise Exception(f'Could not map lists while constructing output. translated_list len: {len(translated_list)} while src_list len: {len(self.src_list)}')

    def get_total_chars(self, list_to_calc):
        '''prints out total characters passed to be proccessed to google translate'''
        chars = 0
        for item in list_to_calc:
            chars = chars + len(item)
        print(f'Calculated total number characters in passed headlines list is {chars}\n')

    def get_translated(self):
        '''if possible, returns translated list'''        
        if self.desired_langs_supported():
            print(f'Extracting headings from headline data lists')
            self.headlines = self.strip_src_to_headings()
            self.get_total_chars(self.headlines)
            print(f'Detecting headlines list language consistency and original language')
            detected_src_lang = self.get_headlines_list_lang(self.headlines)
            # Translate only if detected language is not in target langs list passed as desired_lang_list
            if detected_src_lang not in self.desired_lang_list:    
                print(f'Detected language in passed list: {detected_src_lang}, translating...')
                translated_headlines = self.bulk_translate(self.headlines, detected_src_lang, self.desired_lang_list[0])
                translated_cls_output = self.construct_src_size_output(self.src_list, translated_headlines)
                return translated_cls_output
            else:
                print(f'Returning without translation. Detected lang \'{detected_src_lang}\' already in {self.desired_lang_list}')
                return self.src_list


if __name__ == '__main__':
    pass