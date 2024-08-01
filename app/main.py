from fastapi import FastAPI
app = FastAPI()
import sqlalchemy
from sqlalchemy.pool import NullPool
from sql_dependant import env_init
sql_engine = sqlalchemy.create_engine(
                "mysql://"+env_init.MYSQL_USER+":"+env_init.MYSQL_PASSWORD+"@localhost/"+env_init.MYSQL_DB,
                isolation_level="READ UNCOMMITTED",poolclass=NullPool
                )
import views_api