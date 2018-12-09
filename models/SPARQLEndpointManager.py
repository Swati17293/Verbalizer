from models.LogManager import LogManager
from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLEndpointManager(object):
    sparql = None
    endpoint = ""

    @staticmethod
    def init(endpoint="http://dbpedia.org/sparql"):
        LogManager.LogInfo("Initializing SPARQLEndpointManager...")
        try:
            SPARQLEndpointManager.endpoint = endpoint
            SPARQLEndpointManager.sparql = SPARQLWrapper(endpoint)
        except Exception as e:
            LogManager.LogError("Failed to initialize SPARQLEndpointManager")
            LogManager.LogError(e)
    
    @staticmethod
    def SendQuery(query, returnFormat=JSON):
        LogManager.LogInfo("Sending query to endpoint " + SPARQLEndpointManager.endpoint)
        try:
            SPARQLEndpointManager.sparql.setQuery(query)
            SPARQLEndpointManager.sparql.setReturnFormat(returnFormat)
            results = SPARQLEndpointManager.sparql.query().convert()
            return results
        except Exception as e:
            LogManager.LogError("Unable to Send query to " + SPARQLEndpointManager.endpoint)
            LogManager.LogError(e)
            return None
    
    @staticmethod
    def SendQueryLabel(variable, prefixes='', returnFormat=JSON):
        LogManager.LogInfo(f"Sending query to endpoint {SPARQLEndpointManager.endpoint} for getting label of {variable}")
        query = prefixes + ' SELECT ?label WHERE { ' + variable + ' <http://www.w3.org/2000/01/rdf-schema#label> ' + '?label . }'
        try:
            SPARQLEndpointManager.sparql.setQuery(query)
            SPARQLEndpointManager.sparql.setReturnFormat(returnFormat)
            results = SPARQLEndpointManager.sparql.query().convert()
            return results["results"]["bindings"][0]["label"]["value"]
        except Exception as e:
            LogManager.LogError("Unable to Send query to " + SPARQLEndpointManager.endpoint)
            LogManager.LogError(e)
            return None
