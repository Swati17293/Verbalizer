from models.LogManager import LogManager
from models.LogManager import LogManager
from models.SPARQLEndpointManager import SPARQLEndpointManager
from models.SPARQLParserManager import SPARQLParserManager
from models.DictCCManager import Dict
from models.SplitTextManager import CharSplit
from models.SplitTextManager import SplitWords
from models.Common import Common

class VerbalizeTripleSubject(object):
    def __init__(self, variable, triples, answers, prefixes):
        self.varPos = 0
        self.subjType = self.GetSubjectType(variable, triples, prefixes)
        self.answer = self.GetAnswersLabel(answers)
        self.isNounPlural = True if len(self.answer) > 1 else False
        self.subjWithArticle = self.GetSubjectArtikel(self.subjType)
        self.verb = '' if self.subjWithArticle is '' else \
            'sind' if len(self.answer) > 1 else 'ist'

        self.verbalizedAnswer = self.ConcatenateAnswer(self.subjWithArticle, self.verb, ', '.join(self.answer))
    
    def GetSubjectType(self, variable, triples, prefixes):
        LogManager.LogInfo(f"Getting type of subject...")
        subject = '?' + variable
        subjType = Common.GetSubjectTypeFromTriples(subject, triples)
        if subjType and not subjType[0].startswith('?'):
            return Common.GetUriLastPart(subjType[0]) if 'http' in subjType[0] else Common.GetUriPartWithPrefixes(subjType[0])
        else:
            if 'http' in subject or ':' in subject:
                return SPARQLEndpointManager.SendQueryForLabel(subject, prefixes)
            elif subject.startswith('?'):
                labelTriple = Common.GetTripleWithLabel(subject, triples)
                if not labelTriple:
                    return ''
                else:
                    queryType = SPARQLEndpointManager.SendQueryForType(subject, labelTriple, prefixes)
                    return Common.GetUriLastPart(queryType) if 'http' in queryType else \
                        queryType if queryType is not None else ''
            else:
                return ''
        
    def GetSubjectArtikel(self, type):
        LogManager.LogInfo(f"Getting artikel for subject type...")
        if type == '' or type == None:
            return ''
        else:
            newType = Dict.CheckType(type, self.isNounPlural)
            return newType.title() if any(x in newType for x in Common.germanArticles) else 'Der ' + type
    
    def GetPredicateAnswer(self, variable, triples, answers):
        LogManager.LogInfo(f"Getting main predicate for verbalizer...")
        return ''

    def GetAnswersLabel(self, answers):
        labelAnswers = []
        predicateLabel = Common.einsatzkraftLabel if self.subjType == 'Einsatzkraft' else Common.allRdfLabels[-1]
        if answers:
            if 'http' in answers[0]:
                for answer in answers:
                    queryAnswer = SPARQLEndpointManager.SendQueryForLabel('<' + answer + '>', '', predicateLabel)
                    labelAnswers.append(queryAnswer.strip() if queryAnswer != "" and queryAnswer != None else Common.GetUriLastPart(answer))
            else:
                labelAnswers = answers

        return list(set(labelAnswers))
        
    def ConcatenateAnswer(self, subjWithArticle, predicate, answer):
        LogManager.LogInfo(f"Constructing final verbalized answer...")
        return subjWithArticle + ' ' + str(predicate) + ' ' + str(answer) + '.'
