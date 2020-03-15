from flask import Flask

from .config import config_by_name
from flask_cors import CORS, cross_origin
import flask_excel as excel
import joblib
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from flask_dropzone import Dropzone
import spacy
import os

dropzone = Dropzone()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name['dev'])

    resources_path = os.path.join(app.config.get('APP_STATIC'), 'resources')
    app.resources_path = resources_path + '/'

    print("Loading spell_checker...")
    app.spell_checker = joblib.load(app.resources_path + 'spell_checker.pk')

    print("Loading trigram_counter...")
    app.trigram_counter = joblib.load(app.resources_path + 'trigram_counter_lowercase.pk')

    print("Loading dictionary...")
    app.dictionary = joblib.load(app.resources_path + 'domain_dict.pk')

    print("Loading spaCy...")
    app.nlp = spacy.load('en_core_web_sm')

    print("All loaded")

    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    excel.init_excel(app)
    dropzone.init_app(app)

    return app
