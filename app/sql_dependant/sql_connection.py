from sqlalchemy.orm import Session
from main import sql_engine

class sqlconn:

    def __init__(self):
        self.init_call()

    def __enter__(self):
        self.init_call()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def init_call(self):
        engine = sql_engine
        connection = engine.connect()
        connection = connection.execution_options(
        stream_results=True,
        isolation_level="READ UNCOMMITTED"
)
        self.session = Session(engine)
        self.connection = connection
        
    def execute(self,query):
        try:
            self.session.execute(query)
            return True
        except:
            print("Error in sql query execution. query was:  " + str(query))
            return False
    
    def commit(self):
        try:
            self.session.commit()
            return True
        except:
            print("Error while committing to the database.")
            return False

    def close(self):
        try:
            self.session.invalidate()
            self.connection.close()
        except:
            print("error closing connections")
