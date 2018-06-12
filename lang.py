
import json


class LanguageSupport:
    """Multiple language indexer."""

    def __init__(self, lang='en-US'):
        f = open('lang.json', 'r', encoding='utf-8')
        s = f.read()
        f.close()
        j = json.loads(s)
        self.strings = {}
        if lang not in j['lang']:
            lang = 'en-US'
        for i in j['lang'][lang]:
            self.strings[i] = j['lang'][lang][i]
        return

    def get_text(self, index):
        if index not in self.strings:
            return index
        return self.strings[index]
    pass


language_support = LanguageSupport('en-US')


def text(index):
    return language_support.get_text(index)
