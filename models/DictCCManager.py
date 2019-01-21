import urllib.request as urllib2
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from models.SplitTextManager import CharSplit
from models.Common import Common
import re

# Unoficial dict.cc client
class Dict(object):
    @classmethod
    def Check(cls, word, from_language = 'de', to_language = 'en'):
        response_body = cls.GetResponse(word, from_language, to_language)
        result = cls.ParseResponse(response_body)

        return result

    @classmethod
    def GetResponse(cls, word, from_language, to_language):
        subdomain = from_language.lower()+to_language.lower()
        url = f"https://{subdomain}.dict.cc/?s={quote_plus(word.encode('utf-8'))}"
        req = urllib2.Request(
            url,
            None,
            {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'}
        )
        res = urllib2.urlopen(req).read()
        
        return res.decode("utf-8")

    @classmethod
    def ParseResponse(cls, response_body):
        soup = BeautifulSoup(response_body, "html.parser")
        
        verb = [tds.find_all("a") for tds in soup.find_all("tr", attrs={'title': "infinitive | preterite | pp"})]
        noun = [tds.find_all("a") for tds in soup.find_all("tr", attrs={'title': "article sg | article pl"})]

        if len(verb) > 0 and len(noun) > 0:
            return ['noun', noun]
        elif len(verb) > 0:
            return ['verb', verb]
        elif len(noun) > 0:
            return ['noun', noun]
        else:
            return ['', '']

    @classmethod
    def CheckPredicates(cls, predicates, isVerbInfiniteForm=False, isNounPlural=False, isAccusative=False):
        newPredicates = []
        countVerb = 0
        countNoun = 0
        for pred in predicates:
            dictAnswer = cls.Check(pred)
            if dictAnswer[0] == 'verb':
                dictVerb = dictAnswer[1][0][0].text if isVerbInfiniteForm else pred
                newPredicates.append(dictVerb) 
                countVerb += 1
            elif dictAnswer[0] == 'noun':
                dictNoun = None
                if len(dictAnswer[1]) > 1:
                    for answer in dictAnswer[1]:
                        if dictNoun is None:
                            dictNoun = answer
                        elif not dictNoun[0].text.startswith('der') and answer[0].text.startswith('der'):
                            dictNoun = answer
                    dictNoun = dictNoun[1].text.strip() if isNounPlural else dictNoun[0].text
                else:
                    dictNoun = dictAnswer[1][0][1].text.strip() if isNounPlural else dictAnswer[1][0][0].text
                dictNoun = re.sub(r'\[.*\]', '', dictNoun).strip()
                dictNoun = dictNoun.replace('der', 'den') if 'der' in dictNoun and isAccusative else dictNoun
                newPredicates.append(dictNoun)
                countNoun += 1
            else:
                newPredicates.append(cls.CheckCompoundWords(pred, isNounPlural, isAccusative))
        
        if countVerb == 0:
            predVerb = 'haben' if isVerbInfiniteForm else 'hat'
            newPredicates.insert(0, predVerb)
        
        return newPredicates
    
    @classmethod
    def CheckType(cls, type, isNounPlural=False):
        dictAnswer = cls.Check(type)
        if dictAnswer[0] == 'noun':
            dictNoun = dictAnswer[1][0][1].text.strip() if isNounPlural else dictAnswer[1][0][0].text
            dictNoun = re.sub(r'\[.*\]', '', dictNoun).strip()
            return dictNoun
        else:
            return cls.CheckCompoundWords(type, isNounPlural)
    

    @classmethod
    def CheckCompoundWords(cls, word, isPlural=False, isAccusative=False):
        if any(x in word for x in Common.germanArticles): return word if not 'der' in word and isAccusative else word.replace('der', 'den')
        
        stemWords = CharSplit.SplitCompoundWord(word)
        if not isinstance(stemWords, list): return word
        
        if len(stemWords) != 2: return word
            
        dictAnswer = cls.Check(stemWords[1])
        if dictAnswer[0] != 'noun': return word

        dictNoun = dictAnswer[1][0][1].text.strip() if isPlural else dictAnswer[1][0][0].text
        dictNoun = re.sub(r'\[.*\]', '', dictNoun).strip()
        if not any(x in dictNoun for x in Common.germanArticles): return word

        article, noun = dictNoun.split(' ', 1)
        article = 'den' if article == 'der' and isAccusative else article
        return article + ' ' + stemWords[0].title() + noun.lower()