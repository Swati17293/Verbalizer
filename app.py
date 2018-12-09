from flask import Flask, render_template, request, get_template_attribute
from models.PostgreSQLManager import SQLManager
from models.LogManager import LogManager
from models.XMLManager import XMLManager
from models.SPARQLEndpointManager import SPARQLEndpointManager
from models.VerbalizeManager import VerbalizeManager
import json

LogManager.init()
XMLManager.init()
SPARQLEndpointManager.init("http://127.0.0.1:3030/solide/sparql")
SQLManager.init("solide_queries", 10)

LogManager.LogInfo('Starting Flask Application...') 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', labels=SQLManager.GetRandomLabels(), version=XMLManager.GetLatestVersion())

@app.route('/', methods=['POST'])
def PostRequests():
    if 'query' in request.form :
        sparqlQuery = request.form['query']
        verbilizer = VerbalizeManager(sparqlQuery)
        return str(verbilizer.answer)
    elif 'label' in request.form:
        label = request.form['label']
        queryLabel = SQLManager.GetSpecificQuery(label)
        return queryLabel
    elif 'sample' in request.form:
        sampleQueries = SQLManager.GetRandomLabels()
        return json.dumps(sampleQueries)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')