import psycopg2

class SQLManager(object):
    def __init__(self):
        conn = psycopg2.connect(
            database="rhylhlsw",
            user="rhylhlsw",
            password="9al4oMxAkshZTpLQIrW4261P_cRX_Vur",
            host="nutty-custard-apple.db.elephantsql.com",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT query FROM public.sparql_queries;")
        self.queries = [r[0] for r in cur.fetchall()]
    
    def GetQueries(self):
        return self.queries
