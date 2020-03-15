import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'jhjhiushdmn')
    DEBUG = False
    # __file__ refers to the file settings.py
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    APP_STATIC = os.path.join(APP_ROOT, 'static')
    UPLOADED_PATH=os.path.join(APP_ROOT, 'uploads')
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = '.docx, .py, .txt'
    DROPZONE_MAX_FILE_SIZE=100
    DROPZONE_MAX_FILES=100

class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://infonut1_nutricion:0304mnON$@localhost:3306/infonut1_nutricion'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
