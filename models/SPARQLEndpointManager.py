from models.LogManager import LogManager
from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLEndpointManager(object):
    sparql = None
    endpoint = ""

    @staticmethod
    def init(endpoint="http://dbpedia.org/sparql"):
        LogManager.LogInfo(f"Initializing SPARQLEndpointManager...")
        try:
            SPARQLEndpointManager.endpoint = endpoint
            SPARQLEndpointManager.sparql = SPARQLWrapper(endpoint)
        except Exception as e:
            LogManager.LogError(f"Failed to initialize SPARQLEndpointManager")
            LogManager.LogError(e)
    
    @staticmethod
    def SendQuery(query, returnFormat=JSON):
        LogManager.LogInfo(f"Sending query to endpoint {SPARQLEndpointManager.endpoint}")
        try:
            SPARQLEndpointManager.sparql.setQuery(query)
            SPARQLEndpointManager.sparql.setReturnFormat(returnFormat)
            results = SPARQLEndpointManager.sparql.query().convert()
            return results
        except Exception as e:
            LogManager.LogError(f"Unable to Send query to {SPARQLEndpointManager.endpoint}")
            LogManager.LogError(e)
            return None
    
    @staticmethod
    def SendQueryForLabel(variable, prefixes='', returnFormat=JSON):
        LogManager.LogInfo(f"Sending query to endpoint {SPARQLEndpointManager.endpoint} for getting label of {variable}")
        stringPrefixes = [pref[1] for pref in prefixes] if prefixes != '' else ['']
        query = ' '.join(stringPrefixes) + ' SELECT ?label WHERE { ' + variable + ' <http://www.w3.org/2000/01/rdf-schema#label> ' + '?label . }'
        try:
            SPARQLEndpointManager.sparql.setQuery(query)
            SPARQLEndpointManager.sparql.setReturnFormat(returnFormat)
            results = SPARQLEndpointManager.sparql.query().convert()
            return results["results"]["bindings"][0]["label"]["value"] if len(results["results"]["bindings"]) > 0 else ''
        except Exception as e:
            LogManager.LogError(f"Unable to Send query to {SPARQLEndpointManager.endpoint}")
            LogManager.LogError(e)
            return None
    
    @staticmethod
    def SendQueryForType(variable, labelTriple, prefixes='', returnFormat=JSON):
        LogManager.LogInfo(f"Sending query to endpoint {SPARQLEndpointManager.endpoint} for getting type of {variable}")
        stringLabelTriple = f'{labelTriple[0][0]} {labelTriple[0][1]} "{labelTriple[0][2]}"'
        stringPrefixes = [pref[1] for pref in prefixes] if prefixes != '' else ['']
        query = ' '.join(stringPrefixes) + ' SELECT DISTINCT ?type WHERE { ' + variable + ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ' + '?type . ' + stringLabelTriple + ' } LIMIT 1'
        try:
            SPARQLEndpointManager.sparql.setQuery(query)
            SPARQLEndpointManager.sparql.setReturnFormat(returnFormat)
            results = SPARQLEndpointManager.sparql.query().convert()
            return results["results"]["bindings"][0]["type"]["value"] if len(results["results"]["bindings"]) > 0 else ''
        except Exception as e:
            LogManager.LogError(f"Unable to Send query to {SPARQLEndpointManager.endpoint}")
            LogManager.LogError(e)
            return None
