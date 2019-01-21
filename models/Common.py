from models.LogManager import LogManager


class Common(object):
    allRdfTypes = ['a', 'rdf:type', '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>']
    allRdfLabels = ['rdfs:label', '<http://www.w3.org/2000/01/rdf-schema#label>']
    germanArticles = ['der', 'die', 'das']
    einsatzkraftLabel = '<http://solide-projekt.de/ontology/takteinheit>'
    
    @staticmethod
    def GetUriLastPart(uri):
        return uri.rsplit('/', 1)[-1].lstrip('<').rstrip('>')
    
    @staticmethod
    def GetUriPartWithPrefixes(uri):
        return uri.strip('"').split(':')[1]
    
    @staticmethod
    def GetLabel(label):
        return label.strip('"').split('"')[0]
    
    @staticmethod
    def GetAnswerTriple(var, triples, varPos):
        return [tri for tri in triples if var == tri[varPos]]
    
    @staticmethod
    def GetSubjectTypeFromTriples(subject, triples):
        return [tri[2] for tri in triples if subject == tri[0] and tri[1] in Common.allRdfTypes]

    @staticmethod
    def GetSubjectLabelFromTriples(subject, triples):
        return [tri[2] for tri in triples if subject == tri[0] and tri[1] in Common.allRdfLabels]
    
    @staticmethod
    def GetTripleWithLabel(subject, triples):
        return [tri for tri in triples if subject == tri[0] and tri[1] in Common.allRdfLabels and not tri[2].startswith('?')]