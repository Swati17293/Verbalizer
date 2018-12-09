from models.LogManager import LogManager
from models.SPARQLEndpointManager import SPARQLEndpointManager
from models.SPARQLParserManager import SPARQLParserManager
from models.DictCCManager import Dict
from models.SplitTextManager import CharSplit
from models.SplitTextManager import SplitWords

class VerbalizeManager(object):
    def __init__(self, query):
        LogManager.LogInfo("Starting Verbalize Manager...")
        self.answer = None
        self.parser = SPARQLParserManager(query) 
        if self.parser.queryIsValid:
            self.answer = self.Verbalize(self.parser.queryVariable[0], self.parser.queryTriples, self.parser.queryAnswer, self.parser.queryPrefixes)
        else:
            LogManager.LogError(f"Invalid query syntax for query:\n{query}")
            self.answer = self.parser.queryError
    
    def Verbalize(self, variable, triples, answers, prefixes):
        isVariablePosSubject = self.GetAnswerVariablePosition(variable, triples)
        if isVariablePosSubject == None:
            return f"Verbalizer can only work for subject or object query positions.\n {answers}"
        elif isVariablePosSubject :
            return self.ConstructAnswerForSubject(variable, triples, answers, prefixes)
        else:
            return self.ConstructAnswerForObject(variable, triples, answers, prefixes)
    
    def GetAnswerVariablePosition(self, variable, triples):
        countSubj = 0
        countObj = 0
        var = '?' + variable
        for triple in triples:
            if var == triple[0]:
                countSubj = countSubj + 1
            elif var == triple[2]:
                countObj = countObj + 1
        
        if countSubj == 0 and countObj == 0:
            return None
        elif countSubj > countObj:
            return True
        else:
            return False
    
    def ConstructAnswerForSubject(self, variable, triples, answers, prefixes):
        # TODO...
        return None
    
    def ConstructAnswerForObject(self, variable, triples, answers, prefixes):
        subjType = self.GetSubjectType(variable, triples, prefixes, False)
        artikelType = self.GetTypeArtikel(subjType)
        label = self.GetSubjectLabel(variable, triples, False)
        predicate = self.GetPredicateAnswer(variable, triples, answers, False)
        answer = self.GetAnswersLabel(answers)

        return self.ConcatenateAnswer(artikelType, label, ' '.join(predicate), ', '.join(answer))
    
    def GetSubjectType(self, variable, triples, prefixes, isVariablePosSubject):
        LogManager.LogInfo("Getting type of subject...")
        var = '?' + variable
        allQueryTypes = ['a', 'rdf:type', '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>']
        if isVariablePosSubject:
            # TODO Implement case when query variable is subject
            return ''
        else:
            answerTriple = [tri for tri in triples if var == tri[2]]
            subj = answerTriple[0][0]
            subjType = [tri[2] for tri in triples if subj == tri[0] and tri[1] in allQueryTypes]
            if subjType and not subjType[0].startswith('?'):
                if '<http' in subjType[0]:
                    return subjType[0].rsplit('/', 1)[-1].lstrip('<').rstrip('>')
                else:
                    return subjType[0].lstrip('<').rstrip('>').strip('"').split(':')[1]
            else:
                if 'http' in subj:
                    return SPARQLEndpointManager.SendQueryLabel('<' + subj + '>')
                elif ':' in subj:
                    return SPARQLEndpointManager.SendQueryLabel(subj, prefixes)
                else:
                    return ''
    
    def GetTypeArtikel(self, type):
        LogManager.LogInfo("Getting artikel of subject type...")
        # TODO 
        if type == '' or type == None:
            return ''
        else:
            newType = Dict.CheckType(type)
            if any(x in newType for x in ['der', 'die', 'das']):
                return newType.title()
            else:
                return 'Der ' + type
    
    def GetSubjectLabel(self, variable, triples, isVariablePosSubject):
        LogManager.LogInfo("Getting label of subject...")
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
                # TODO Send query to endpoint to get label, if there is no label extract last part of URI and use as label
                return ''
    
    def GetPredicateAnswer(self, variable, triples, answers, isVariablePosSubject):
        LogManager.LogInfo("Getting main predicate for verbalizer...")
        var = '?' + variable
        isNounPlural = True if len(answers) > 1 else False
        isVerbInfiniteForm = True if len(answers) > 1 and isVariablePosSubject else False
        if isVariablePosSubject:
            # TODO Implement case when query variable is subject
            return ''
        else:
            answerTriple = [tri for tri in triples if var == tri[2]]
            predicate = answerTriple[0][1]
            if predicate != None:
                if '<http' in predicate:
                    predicate = predicate.rsplit('/', 1)[-1].lstrip('<').rstrip('>')
                else:
                    predicate = predicate.strip('"').split(':')[1]
                
                if '_' in predicate: 
                    return Dict.CheckPredicates(predicate.split('_'), isVerbInfiniteForm, isNounPlural)

                # splitPredicate = CharSplit.SplitCompoundWord(predicate)
                splitPredicate = SplitWords.split(predicate)
                if splitPredicate == predicate:
                    return Dict.CheckPredicates([predicate], isVerbInfiniteForm, isNounPlural)
                else:
                    return Dict.CheckPredicates([word.lower() for word in splitPredicate], isVerbInfiniteForm, isNounPlural)
            else:
                return ''

        # TODO Split predicate if it consists from more than 2 words
        return predicate

    def GetAnswersLabel(self, answers):
        labelAnswers = []
        if answers:
            if 'http' in answers[0]:
                for answer in answers:
                    queryAnswer = SPARQLEndpointManager.SendQueryLabel('<' + answer + '>')
                    if queryAnswer != "" and queryAnswer != None:
                        labelAnswers.append(queryAnswer.strip())
                    else:
                        labelAnswers.append(answer.rsplit('/', 1)[-1].lstrip('<').rstrip('>'))
            else:
                labelAnswers = answers

        return labelAnswers

        
    def ConcatenateAnswer(self, artikelType, label, predicate, answers):
        LogManager.LogInfo("Constructing final verbalized answer...")
        return artikelType + ' ' + label + ' ' + str(predicate) + ' [' + str(answers) + '].'
    
    def NLP(self):
        # TODO If we have time, Use spacy for basic NLP methods to improve verbalizer answer
        return None