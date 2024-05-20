import flask
from flask_cors import CORS
app = flask.Flask(__name__)
cors = CORS(app, supports_credentials=True,resources={r"*": {"origins": "*"}})
#For sql required stuff.
import sqlalchemy
from sqlalchemy.pool import NullPool
from app.sql_dependant import env_init
app.config['SECRET_KEY'] = env_init.SECRET_KEY
app.json.ensure_ascii = False # for weird json not rendering "ş" etc.
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # maximum uploaded jpg size of 2 megabytes.
sql_engine = sqlalchemy.create_engine(
                "mysql://"+env_init.MYSQL_USER+":"+env_init.MYSQL_PASSWORD+"@localhost/"+env_init.MYSQL_DB,
                isolation_level="READ UNCOMMITTED",poolclass=NullPool
                )
