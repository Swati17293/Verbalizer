import psycopg2

class SQLManager(object):
    def __init__(self):
        with open('postgre-password.txt', 'r') as passwordFile:
            password = passwordFile.read()

        conn = psycopg2.connect(
            database="rhylhlsw",
            user="rhylhlsw",
            password=password,
            host="nutty-custard-apple.db.elephantsql.com",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT query FROM public.sparql_queries;")
        self.queries = [r[0] for r in cur.fetchall()]
    
    def GetQueries(self):
        return self.queries
