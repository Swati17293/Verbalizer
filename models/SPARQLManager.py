from models.LogManager import LogManager
from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLManager(object):
    sparql = None

    @staticmethod
    def init(endpoint="http://dbpedia.org/sparql"):
        LogManager.LogInfo("Initializing SPARQLManager...")
        SPARQLManager.sparql = SPARQLWrapper(endpoint)
    
    @staticmethod
    def SendQuery(query, returnFormat=JSON):
        LogManager.LogInfo("Sending query to endpoint...")
        try:
            SPARQLManager.sparql.setQuery(query)
            SPARQLManager.sparql.setReturnFormat(returnFormat)
            results = SPARQLManager.sparql.query().convert()
            return results
        except:
            LogManager.LogError("Unable to Send query")
            return None
