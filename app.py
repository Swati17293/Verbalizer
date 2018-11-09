from flask import Flask, render_template, request, get_template_attribute
from models.PostgreSQLManager import SQLManager
from models.LogManager import LogManager
from models.XMLManager import XMLManager
from models.SPARQLManager import SPARQLManager
import json

LogManager.init()
XMLManager.init()
SPARQLManager.init()

LogManager.LogInfo('Starting Flask Application...') 

app = Flask(__name__)

SQLManager.init()

@app.route('/')
def index():
    return render_template('index.html', labels=SQLManager.GetRandomLabels(), version=XMLManager.GetLatestVersion())

@app.route('/', methods=['POST'])
def PostRequests():
    if 'query' in request.form :
        sparqlQuery = request.form['query']
        answer = SPARQLManager.SendQuery(sparqlQuery)
        return json.dumps(answer)
    elif 'label' in request.form:
        label = request.form['label']
        queryLabel = SQLManager.GetSpecificQuery(label)
        return queryLabel
    elif 'sample' in request.form:
        sampleQueries = SQLManager.GetRandomLabels()
        return json.dumps(sampleQueries)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')