from models.LogManager import LogManager
from models.SPARQLEndpointManager import SPARQLEndpointManager
from urllib.parse import urlparse
import re, shlex


class SPARQLParserManager(object):
    def __init__(self, query):
        self.queryIsValid = False
        self.queryError = ""
        self.queryVariable = None
        self.queryAnswer = None
        self.queryTriples = None
        self.queryPrefixes = None
        self.ParseQuery(query)
        
    
    def ParseQuery(self, query):
        LogManager.LogInfo(f"Parsing SPARQL query...")
        self.queryIsValid = self.ValidateQuery(query)
        self.serverAnswer = SPARQLEndpointManager.SendQuery(query)
        if self.serverAnswer is None: self.queryIsValid = False
        if self.queryIsValid: 
            self.queryPrefixes = self.GetQueryPrefixes(query)
            self.queryTriples = self.GetQueryTriples(query)
            if self.queryIsValid:
                self.queryVariable = self.GetQueryVariables()
                if len(self.queryVariable) == 1:
                    self.queryAnswer = self.GetQueryAnswers()
                    if self.queryAnswer == None:
                        self.queryIsValid = False
                        self.queryError = f"Die Abfrage hat keine Antwort."
                else:
                    self.queryIsValid = False
                    self.queryError = f"Sie können nur eine Variable abfragen. {self.queryVariable}\nAbfragen Antwort: {self.serverAnswer}"
        else:
            self.queryError = f"Ungültige Abfragesyntax."
        

    def ValidateQuery(self, query):
        LogManager.LogInfo(f"Validating query: {query}")
        inlineQuery = query.replace('\n', ' ').replace('\t', '').replace(' ', '')
        queryRegex = r'(.*)[Ss][Ee][Ll][Ee][Cc][Tt](.*)[Ww][Hh][Ee][Rr][Ee]{(.*)}(.*)'
        matchQuery = re.match(queryRegex, inlineQuery)
        if matchQuery:
            LogManager.LogInfo(f"Query structure is valid")
            return True
        else:
            return False
    
    def GetQueryVariables(self):
        LogManager.LogInfo(f"Extracting query variable from endpoint answer...")
        return self.serverAnswer["head"]["vars"]
    
    def GetQueryAnswers(self):
        LogManager.LogInfo(f"Getting query answer from endpoint...")
        answers = []
        for result in self.serverAnswer["results"]["bindings"]:
            answers.append(result[self.queryVariable[0]]["value"])
        
        if len(answers) == 0:
            LogManager.LogInfo(f"No answer from endpoint")
            return None
        
        return answers
    
    def GetQueryTriples(self, query):
        LogManager.LogInfo(f"Extracting triples from query...")
        triples = []
        inlineQuery = query.replace('\n', ' ').replace('\t', '')
        allTriples = inlineQuery[inlineQuery.find("{")+1:inlineQuery.find("}")]
        allTriples = re.sub(r'\([^)]*\)', '', allTriples)
        removeFilter = re.compile(re.escape('filter'), re.IGNORECASE)
        allTriples = removeFilter.sub('', allTriples)
        nTriples = [i for i in shlex.split(allTriples) if i != '.']

        if len(nTriples) % 3 != 0:
            self.queryIsValid = False
            self.queryError = f"Invalid triples format on query: {nTriples}"
            LogManager.LogInfo(self.queryError)
            return None
        
        triplesNum = len(nTriples) // 3
        for i in range(triplesNum + 1):
            if i != 0:
                i = (i * 3) - 1
                sub = nTriples[i-2]
                pred = nTriples[i-1]
                obj = nTriples[i]
                triples.append((sub, pred, obj))

        LogManager.LogInfo(f"Triples extracted successfully! Triples: {triples}")
        return triples
    
    def GetQueryPrefixes(self, query):
        LogManager.LogInfo(f"Extracting prefixes from query...")
        prefixes = []
        inlineQuery = query.replace('\n', ' ').replace('\t', '')
        queryRegex = r'(.*)[Ss][Ee][Ll][Ee][Cc][Tt](.*)'
        matchPrefixes = re.match(queryRegex, inlineQuery)

        if not matchPrefixes:
            LogManager.LogInfo(f"No prefixes found")
            return None

        allPrefixes = matchPrefixes.group(1)
        nPrefixes = [i.lstrip(' ') for i in allPrefixes.split('>') if i != ' ']
        nPrefixes = [i+'>' for i in nPrefixes if i != '']

        for prefix in nPrefixes:
            prefxRegex = '[Pp][Rr][Ee][Ff][Ii][Xx](.*?):'
            matchPrefix = re.match(prefxRegex, prefix)
            if not matchPrefix:
                LogManager.LogError("Invalid Prefixes")
                return None
            prefixes.append((matchPrefix.group(1).lstrip(' '), prefix))

        LogManager.LogInfo(f"Prefixes extracted successfully! Prefixes: {prefixes}")
        return prefixes
    
    def GetFilterPattern(self, query):
        # TODO...
        return None
    
    def GetOrderByModifier(self, query):
        # TODO...
        return None
    
    def GetLimitModifier(self, query):
        # TODO...
        return None
