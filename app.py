from flask import Flask, render_template
from models.PostgreSQLManager import SQLManager
from models.LogManager import LogManager
from models.XMLManager import XMLManager

LogManager.init()
XMLManager.init()

LogManager.LogInfo('Starting Flask Application...') 

app = Flask(__name__)

SQLManager.init()

@app.route('/')
def index():
    return render_template('index.html', queries=SQLManager.GetQueries(), version=XMLManager.GetLatestVersion())
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')