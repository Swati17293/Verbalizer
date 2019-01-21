from models.LogManager import LogManager
from models.SPARQLEndpointManager import SPARQLEndpointManager
from models.SPARQLParserManager import SPARQLParserManager
from models.DictCCManager import Dict
from models.SplitTextManager import CharSplit
from models.SplitTextManager import SplitWords
from models.Common import Common

class VerbalizeTripleObject(object):
    def __init__(self, variable, triples, answers, prefixes):
        self.varPos = 2
        self.isNounPlural = True if len(answers) > 1 else False
        self.isVerbInfiniteForm = False
        self.isAccusative = True
        self.subjType = self.GetSubjectType(variable, triples, prefixes)
        self.subjWithArticle = self.GetSubjectArtikel(self.subjType)
        self.subjLabel = self.GetSubjectLabel(variable, triples)
        self.predicate = self.GetPredicateAnswer(variable, triples, answers)
        self.answer = self.GetAnswersLabel(answers)

        self.verbalizedAnswer = self.ConcatenateAnswer(self.subjWithArticle, self.subjLabel, self.predicate, self.answer)    
    def GetSubjectType(self, variable, triples, prefixes):
        LogManager.LogInfo(f"Getting type of subject...")
        var = '?' + variable
        answerTriple = Common.GetAnswerTriple(var, triples, self.varPos)
        subject = answerTriple[0][0]
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
            newType = Dict.CheckType(type)
            return newType.title() if any(x in newType for x in Common.germanArticles) else 'Der ' + type

    def GetSubjectLabel(self, variable, triples):
        LogManager.LogInfo(f"Getting label for subject...")
        var = '?' + variable
        answerTriple = Common.GetAnswerTriple(var, triples, self.varPos)
        subject = answerTriple[0][0]
        subjectLabel = Common.GetSubjectLabelFromTriples(subject, triples)
        if subjectLabel:
            if not subjectLabel[0].startswith('?'):
                return Common.GetLabel(subjectLabel[0])
            else:
                # TODO label should be somewhere in query e.g. FILTER, use regex to extract it
                return ''
        elif 'http' in subject:
            return Common.GetUriLastPart(subject)
        elif ':' in subject:
            return Common.GetUriPartWithPrefixes(subject)
        else:
            # TODO Send query to endpoint to get label
            return ''
    
    def GetPredicateAnswer(self, variable, triples, answers):
        # TODO Split predicate if it consists from more than 2 words
        LogManager.LogInfo(f"Getting main predicate for verbalizer...")
        var = '?' + variable
        answerTriple = Common.GetAnswerTriple(var, triples, self.varPos)
        predicate = answerTriple[0][1]
        if predicate != None:
            predicate = Common.GetUriLastPart(predicate) if 'http' in predicate else Common.GetUriPartWithPrefixes(predicate)
            if '_' in predicate: return Dict.CheckPredicates(predicate.split('_'), self.isVerbInfiniteForm, self.isNounPlural, self.isAccusative)
            splitPredicate = SplitWords.split(predicate)
            return Dict.CheckPredicates([predicate], self.isVerbInfiniteForm, self.isNounPlural, self.isAccusative) if splitPredicate == predicate else Dict.CheckPredicates([word.lower() for word in splitPredicate], self.isVerbInfiniteForm, self.isNounPlural, self.isAccusative)
        else:
            return ''

    def GetAnswersLabel(self, answers):
        labelAnswers = []
        if answers:
            if 'http' in answers[0]:
                for answer in answers:
                    queryAnswer = SPARQLEndpointManager.SendQueryForLabel('<' + answer + '>')
                    labelAnswers.append(queryAnswer.strip() if queryAnswer != "" and queryAnswer != None else Common.GetUriLastPart(answer))
            else:
                labelAnswers = answers

        return labelAnswers
        
    def ConcatenateAnswer(self, subjWithArticle, subjLabel, predicate, answer):
        LogManager.LogInfo(f"Constructing final verbalized answer...")
        predicate = ' '.join(predicate)
        answer = ', '.join(answer) if len(answer) < 5 else '\n'.join(answer)
        return subjWithArticle + ' ' + subjLabel + ' ' + str(predicate) + ' ' + str(answer) + '.'