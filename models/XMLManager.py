import xml.etree.ElementTree as ET
from models.LogManager import LogManager
import random

class XMLManager(object):
    latestVersion = None
    queries = []
    labels = []
    sampleQueriesNum = None

    @staticmethod 
    def init(queriesNum=10):
        LogManager.LogInfo(f"Initializing XMLManager and getting latest version and queries...")
        try:
            VersionHistory = ET.parse('VersionHistory.xml')
            Versions = [Version for Version in VersionHistory.findall('Version')]
            XMLManager.latestVersion = Versions[-1].attrib['ID']
        except IOError:
            LogManager.LogError(f"Unable to get latest version from file")
        
        try:
            XMLManager.sampleQueriesNum = queriesNum
            SolideQueries = ET.parse('queries.xml')
            XMLManager.queries = [(question[0].text, question[1].text) for question in SolideQueries.findall('question')]
            XMLManager.labels = [label[0] for label in XMLManager.queries]
        except IOError:
            LogManager.LogError(f"Unable to get queries from file")

    @staticmethod
    def GetLatestVersion():
        return XMLManager.latestVersion
    
    @staticmethod
    def GetQueries():
        return XMLManager.queries
    
    @staticmethod
    def GetLabels():
        return XMLManager.labels
    
    @staticmethod
    def GetRandomLabels():
        return random.sample(set(XMLManager.labels), XMLManager.sampleQueriesNum)

    @staticmethod
    def GetSpecificQuery(label):
        return dict(XMLManager.queries)[label]