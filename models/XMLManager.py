import xml.etree.ElementTree as ET
from models.LogManager import LogManager

class XMLManager(object):
    latestVersion = None

    @staticmethod 
    def init():
        LogManager.LogInfo("Initializing XMLManager and getting latest version...")
        try:
            VersionHistory = ET.parse('VersionHistory.xml')
            Versions = [Version for Version in VersionHistory.findall('Version')]
            XMLManager.latestVersion = Versions[-1].attrib['ID']
        except IOError:
            LogManager("Unable to get latest version from file")

    @staticmethod
    def GetLatestVersion():
        return XMLManager.latestVersion