# alternative translators, if needed

"""
from deep_translator import (GoogleTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             DeepL,
                             QCRI,
                             single_detection,
                             batch_detection)
                             """
from deep_translator import GoogleTranslator

from params import *


def translate(text, source_lang='auto', target_lang=None):
    try:
        if target_lang is None:
            target_lang = PARAMS['TARGET_LANG']
        translated = GoogleTranslator(
            source=source_lang,
            target=target_lang).translate(text=text)
        return translated
    except:
        return text
