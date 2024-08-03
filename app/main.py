from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import sqlalchemy
from sqlalchemy.pool import NullPool
from sql_dependant import env_init
sql_engine = sqlalchemy.create_engine(
                "mysql://"+env_init.MYSQL_USER+":"+env_init.MYSQL_PASSWORD+"@localhost/"+env_init.MYSQL_DB,
                isolation_level="READ UNCOMMITTED",poolclass=NullPool
                )

import views_api