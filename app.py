from flask import Flask, render_template
from PostgreSQLManager import SQLManager
 
app = Flask(__name__)

sampleQueries = SQLManager()

 
@app.route('/')
def index():
    return render_template('index.html', queries=sampleQueries.queries)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')