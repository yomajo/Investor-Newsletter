from googletrans import Translator, LANGUAGES


class TranslateList():
    '''Based on googletrans Translator, tailored for project needs. Works on uniform language list only. Takes args:
    - src_list - scrapped results (list of lists), where first member of each list is string headline sentence
    - desired_lang_list - list of desired output languages (target lang is first member in list)'''

    def __init__(self, src_list, desired_lang_list):
        self.src_list = src_list
        self.desired_lang_list = desired_lang_list
        self.translator = Translator()

    def desired_langs_supported(self):
        '''check if desired languages are supported by googletrans package'''
        for lang in self.desired_lang_list:
            if lang not in LANGUAGES:
                print(f'Provided target language: {lang} is not supported by googletrans library')
                raise Exception
        return True

    def strip_src_to_headings(self):
        '''returns a flat list of headlines extracted from list of lists'''
        headings = []
        for headline_data in self.src_list:
            headings.append(headline_data[0])
        print(f'Formed a stripped list of headlines only. Source list length: {len(self.src_list)}, new list length: {len(headings)}')
        return headings

    def get_headlines_list_lang(self, raw_headlines_list):
        '''returns detected lang of passed list'''
        detected_lang_objs = self.translator.detect(raw_headlines_list)
        confidence_sum = 0
        detected_langs = []
        for detect_obj in detected_lang_objs:
            if detect_obj.lang not in detected_langs:
                detected_langs.append(detect_obj.lang)
                confidence_sum = confidence_sum + detect_obj.confidence
        if len(detected_langs) != 1:
            print(f'Passed list contains more than one language. Detected languages contain: {detected_langs}')
            raise Exception
        confidence = confidence_sum / len(raw_headlines_list)
        print(f'Passed list members are of same language, detection confidence level: {confidence}')
        return detected_langs[0]

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
            print(f'Could not map lists while constructing output. translated_list len: {len(translated_list)} while src_list len: {len(self.src_list)}')
            raise Exception

    def get_translated(self):
        '''returns translated list if src is not yet in desired lang'''
        if self.desired_langs_supported():
            print(f'Extracting headings from headline data lists')
            self.headlines = self.strip_src_to_headings()
            print(f'Detecting headlines list language consistency and original language')
            detected_src_lang = self.get_headlines_list_lang(self.headlines)
            # Translate only if detected language is not in target langs list passed as desired_lang_list
            if detected_src_lang not in self.desired_lang_list:    
                print(f'Detected language in passed list: {detected_src_lang}, translating...')
                translated_headlines = self.bulk_translate(self.headlines, detected_src_lang, self.desired_lang_list[0])
                translated_cls_output = self.construct_src_size_output(self.src_list, translated_headlines)
                return translated_cls_output
            else:
                print(f'Returning without translation. Detected lang {detected_src_lang} already in {self.desired_lang_list}')
                return self.src_list


if __name__ == '__main__':
    pass