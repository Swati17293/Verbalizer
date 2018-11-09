import psycopg2
import random
from models.LogManager import LogManager

class SQLManager(object):
    queries = []
    labels = []
    
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
                cur.execute("SELECT label, query FROM public.qald_queries;")
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
    def GetRandomLabels(num):
        return random.sample(set(SQLManager.labels), num)
