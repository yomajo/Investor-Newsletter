from googletrans import Translator, LANGUAGES
from collections import Counter


class TranslateList():
    '''Based on googletrans Translator, tailored for project needs. Takes args:
    - src_list - bulk translation object THAT IS UNIFORM lang across all its members
    - desired_lang_list - list of desired output languages (target lang is first member in list)'''

    def __init__(self, src_list, desired_lang_list):
        self.src_list = src_list
        self.desired_lang_list = desired_lang_list
        self.translator = Translator()
        self.check_desired_langs()

    def check_desired_langs(self):
        '''check if desired languages are supported by googletrans package'''
        