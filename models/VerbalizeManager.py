from models.LogManager import LogManager
from models.SPARQLEndpointManager import SPARQLEndpointManager
from models.SPARQLParserManager import SPARQLParserManager
from models.DictCCManager import Dict
from models.SplitTextManager import CharSplit
from models.SplitTextManager import SplitWords

class VerbalizeManager(object):
    def __init__(self, query):
        LogManager.LogInfo(f"Starting Verbalize Manager...")
        self.answer = None
        self.parser = SPARQLParserManager(query) 
        if self.parser.queryIsValid:
            self.answer = self.Verbalize(self.parser.queryVariable[0], self.parser.queryTriples, self.parser.queryAnswer, self.parser.queryPrefixes)
        else:
            LogManager.LogError(f"Invalid query syntax for query:\n{query}")
            self.answer = self.parser.queryError
    
    def Verbalize(self, variable, triples, answers, prefixes):
        isVariablePosSubject = self.GetAnswerVariablePosition(variable, triples)
        return f"Verbalizer can only work for subject or object query positions.\n {answers}" if isVariablePosSubject is None else \
         self.ConstructAnswerForSubject(variable, triples, answers, prefixes) if isVariablePosSubject else self.ConstructAnswerForObject(variable, triples, answers, prefixes)
    
    def GetAnswerVariablePosition(self, variable, triples):
        countSubj = 0
        countObj = 0
        var = '?' + variable
        for triple in triples:
            if var == triple[0]: countSubj += 1
            if var == triple[2]: countObj += 1
        
        return None if countSubj == 0 and countObj == 0 else \
            True if countSubj > countObj else False
    
    def ConstructAnswerForSubject(self, variable, triples, answers, prefixes):
        # TODO...
        return None
    
    def ConstructAnswerForObject(self, variable, triples, answers, prefixes):
        subjType = self.GetSubjectType(variable, triples, prefixes, False)
        subjWithArticle = self.GetSubjectArtikel(subjType)
        subjLabel = self.GetSubjectLabel(variable, triples, False)
        predicate = self.GetPredicateAnswer(variable, triples, answers, False)
        answer = self.GetAnswersLabel(answers)

        return self.ConcatenateAnswer(subjWithArticle, subjLabel, ' '.join(predicate), ', '.join(answer))
    
    def GetSubjectType(self, variable, triples, prefixes, isVariablePosSubject):
        LogManager.LogInfo(f"Getting type of subject...")
        var = '?' + variable
        allRdfTypes = ['a', 'rdf:type', '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>']
        allRdfLabels = ['rdfs:label', '<http://www.w3.org/2000/01/rdf-schema#label>']
        if isVariablePosSubject:
            # TODO Implement case when query variable is subject
            return ''
        else:
            answerTriple = [tri for tri in triples if var == tri[2]]
            subj = answerTriple[0][0]
            subjType = [tri[2] for tri in triples if subj == tri[0] and tri[1] in allRdfTypes]
            if subjType and not subjType[0].startswith('?'):
                return subjType[0].rsplit('/', 1)[-1].lstrip('<').rstrip('>') if '<http' in subjType[0] else subjType[0].strip('"').split(':')[1]
            else:
                if 'http' in subj or ':' in subj:
                    return SPARQLEndpointManager.SendQueryForLabel(subj, prefixes)
                elif subj.startswith('?'):
                    labelTriple = [tri for tri in triples if subj == tri[0] and tri[1] in allRdfLabels and not tri[2].startswith('?')]
                    if not labelTriple:
                        return ''
                    else:
                        queryType = SPARQLEndpointManager.SendQueryForType(subj, labelTriple, prefixes)
                        return queryType.rsplit('/', 1)[-1] if 'http' in queryType else \
                            queryType if queryType is not None else ''
                else:
                    return ''
    
    def GetSubjectArtikel(self, type):
        LogManager.LogInfo(f"Getting artikel for subject type...")
        if type == '' or type == None:
            return ''
        else:
            newType = Dict.CheckType(type)
            return newType.title() if any(x in newType for x in ['der', 'die', 'das']) else 'Der ' + type
    
    def GetSubjectLabel(self, variable, triples, isVariablePosSubject):
        LogManager.LogInfo(f"Getting label for subject...")
        var = '?' + variable
        allQueryLabels = ['rdfs:label', '<http://www.w3.org/2000/01/rdf-schema#label>']
        if isVariablePosSubject:
            # TODO Implement case when query variable is subject
            return ''
        else:
            answerTriple = [tri for tri in triples if var == tri[2]]
            subj = answerTriple[0][0]
            subjLabel = [tri[2] for tri in triples if subj == tri[0] and tri[1] in allQueryLabels]
            if subjLabel:
                if not subjLabel[0].startswith('?'):
                    return subjLabel[0].strip('"').split('"')[0]
                else:
                    # TODO label should be somewhere in query e.g. FILTER, use regex to extract it
                    return ''
            elif '<http' in subj:
                return subj.rsplit('/', 1)[-1].lstrip('<').rstrip('>')
            elif ':' in subj:
                return subj.strip('"').split(':')[1]
            else:
                # TODO Send query to endpoint to get label
                return ''
    
    def GetPredicateAnswer(self, variable, triples, answers, isVariablePosSubject):
        LogManager.LogInfo(f"Getting main predicate for verbalizer...")
        var = '?' + variable
        isNounPlural = True if len(answers) > 1 else False
        isVerbInfiniteForm = True if len(answers) > 1 and isVariablePosSubject else False
        isAccusative = True
        if isVariablePosSubject:
            # TODO Implement case when query variable is subject
            return ''
        else:
            answerTriple = [tri for tri in triples if var == tri[2]]
            predicate = answerTriple[0][1]
            if predicate != None:
                predicate = predicate.rsplit('/', 1)[-1].lstrip('<').rstrip('>') if 'http' in predicate else predicate.strip('"').split(':')[1]
                if '_' in predicate: return Dict.CheckPredicates(predicate.split('_'), isVerbInfiniteForm, isNounPlural, isAccusative)
                splitPredicate = SplitWords.split(predicate)
                return Dict.CheckPredicates([predicate], isVerbInfiniteForm, isNounPlural, isAccusative) if splitPredicate == predicate else Dict.CheckPredicates([word.lower() for word in splitPredicate], isVerbInfiniteForm, isNounPlural, isAccusative)
            else:
                return ''

        # TODO Split predicate if it consists from more than 2 words
        return predicate

    def GetAnswersLabel(self, answers):
        labelAnswers = []
        if answers:
            if 'http' in answers[0]:
                for answer in answers:
                    queryAnswer = SPARQLEndpointManager.SendQueryForLabel('<' + answer + '>')
                    labelAnswers.append(queryAnswer.strip() if queryAnswer != "" and queryAnswer != None else answer.rsplit('/', 1)[-1].lstrip('<').rstrip('>'))
            else:
                labelAnswers = answers

        return labelAnswers

        
    def ConcatenateAnswer(self, subjWithArticle, subjLabel, predicate, answer):
        LogManager.LogInfo(f"Constructing final verbalized answer...")
        return subjWithArticle + ' ' + subjLabel + ' ' + str(predicate) + ' ' + str(answer) + '.'
    
    def NLP(self):
        # TODO If we have time, Use spacy for basic NLP methods to improve verbalizer answer
        return None