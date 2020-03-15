from flask_restplus import Api
from flask import Blueprint

from .main.controller.analysis_controller import api as analysis_ns
from .main.controller.testing_controller import api as testing_ns
from .main.controller.views_controller import bp as views_bp

api_blueprint = Blueprint('api', __name__)
views_blueprint = views_bp

api = Api(api_blueprint,
          title='Med Grammar',
          version='1.0',
          description='Context Specific Grammar/Semantic Tools'
          )

api.add_namespace(analysis_ns, path='/analysis')
api.add_namespace(testing_ns, path='/testing')
