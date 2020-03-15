from flask import request
from flask_restplus import Resource

from ..util.dto import AnalysisDto
from ..service.analysis_service import analyze_text, check_spelling, get_triples

api = AnalysisDto.api
_span = AnalysisDto.span
_flagged_item = AnalysisDto.flagged_item

@api.route('/check')
class GrammarCheck(Resource):
    @api.doc('Analyse a block of text and obtain errors')
    @api.marshal_with(_flagged_item, envelope="flagged_items")
    def post(self):
        """Analyse a block of text and obtain errors"""
        data = request.json
        return analyze_text(data)

@api.route('/spelling')
class SpellCheck(Resource):
    @api.doc('Return spelling suggestions for the provided word')
    #@api.marshal_with(String, envelope="suggestions")
    def post(self):
        """Return spelling suggestions for the provided word"""
        data = request.json
        return check_spelling(data)

@api.route('/trigrams')
class GetTrigrams(Resource):
    @api.doc('Return all trigrams containing the the provided word')
    #@api.marshal_with(String, envelope="suggestions")
    def post(self):
        """Return all trigrams containing the the provided word"""
        data = request.json
        return get_triples(data)
