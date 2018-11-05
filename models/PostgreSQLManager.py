import psycopg2
from models.LogManager import LogManager

class SQLManager(object):
    queries = None
    
    @staticmethod
    def init():
        LogManager.LogInfo("Connecting to database...")
        password = None
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
                cur.execute("SELECT query FROM public.sparql_queries;")
                SQLManager.queries = [r[0] for r in cur.fetchall()]
                LogManager.LogInfo("Connected to database successfully!")
            except:
                LogManager.LogError("Failed to connect to database")

    @staticmethod
    def GetQueries():
        return SQLManager.queries
