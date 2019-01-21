from models.LogManager import LogManager
from models.SPARQLParserManager import SPARQLParserManager
from models.VerbalizeTripleSubject import VerbalizeTripleSubject
from models.VerbalizeTripleObject import VerbalizeTripleObject
from models.Common import Common

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

        return answers if isVariablePosSubject is None else \
            VerbalizeTripleSubject(variable, triples, answers, prefixes).verbalizedAnswer if isVariablePosSubject else VerbalizeTripleObject(variable, triples, answers, prefixes).verbalizedAnswer
    
    def GetAnswerVariablePosition(self, variable, triples):
        countSubj = 0
        countObj = 0
        var = '?' + variable
        for triple in triples:
            if var == triple[0]: countSubj += 1
            if var == triple[2]: countObj += 1
            if len(triples) > 1 and var == triple[2] and (triple[1] in Common.allRdfTypes or triple[1] in Common.allRdfLabels):
                countObj -= 1
                countSubj += 1
        
        return None if countSubj == 0 and countObj == 0 else \
            True if countSubj > countObj else False