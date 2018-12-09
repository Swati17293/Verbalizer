from models.LogManager import LogManager
import psycopg2, random

class SQLManager(object):
    queries = []
    labels = []
    sampleQueriesNum = None
    
    @staticmethod
    def init(table, sampleNumber):
        LogManager.LogInfo("Connecting to database...")
        whereClause = "WHERE id IN (1,2,5,6,9,10,13,14,15,16,19,20,23,24,26,27,28,29,35,36,39,40,44,45,50,51,52,53,56,57,61)"
        password = None
        SQLManager.sampleQueriesNum = sampleNumber
        try:
            LogManager.LogInfo("Getting password from file...")
            with open('postgre-password.txt', 'r') as passwordFile:
                password = passwordFile.read()
        except IOError:
            LogManager.LogError("Failed to get password from file")
        
        if(password != None):
            try: 
                conn = psycopg2.connect(
                    database="rhylhlsw",
                    user="rhylhlsw",
                    password=password,
                    host="nutty-custard-apple.db.elephantsql.com",
                    port="5432"
                )
                cur = conn.cursor()
                cur.execute(f"SELECT label, query FROM public.{table} {whereClause};")
                SQLManager.queries = [r for r in cur.fetchall()]
                SQLManager.labels = [query[0] for query in SQLManager.queries]
                LogManager.LogInfo("Connected to database successfully!")
            except:
                LogManager.LogError("Failed to connect to database")

    @staticmethod
    def GetQueries():
        return SQLManager.queries
    
    @staticmethod
    def GetLabels():
        return SQLManager.labels
    
    @staticmethod
    def GetRandomLabels():
        return random.sample(set(SQLManager.labels), SQLManager.sampleQueriesNum)

    @staticmethod
    def GetSpecificQuery(label):
        return dict(SQLManager.queries)[label]
