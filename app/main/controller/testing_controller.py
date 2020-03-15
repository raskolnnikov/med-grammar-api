from flask import request
from flask_restplus import Resource
from flask import render_template, make_response
from ..util.dto import TestingDto
from ..service.testing_service import test_logic, parse_test_instance

api = TestingDto.api



@api.route('/evaluate')
class EvaluatePerformance(Resource):
    @api.doc('Analyse a block of text and obtain errors')
    #@api.marshal_with(_flagged_item, envelope="items")
    def post(self):
        """Analyse a block of text and obtain errors"""
        if request.method == 'POST':
            files = glob.glob(current_app.config['UPLOADED_PATH']+"/test*.txt")
            files.sort(key=os.path.getmtime, reverse=True)
            print(files)
            results = []
            for f in files:
                text, span_list = parse_test_instance(f)
                results.append(
                    test_logic(
                        text,
                        span_list,
                        current_app.trigram_counter,
                        current_app.spell_checker
                    )
                )
                os.remove(f)
            global_metrics = get_global_metrics(results)
            return render_template('text/test.html', called=True, results=results, global_metrics=global_metrics, files=files )
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('text/test.html', called=False, c=0),200,headers)
