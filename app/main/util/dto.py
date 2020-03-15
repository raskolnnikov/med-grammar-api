from flask_restplus import Namespace, fields

class AnalysisDto:
    api = Namespace('analysis', description='Contains all the analysis-related operations')
    span = api.model('span', {
        'text': fields.String(),
        'start_idx': fields.Integer(),
        'end_idx': fields.Integer(),
        'dist_from_first': fields.Integer(),
        'dist_from_last': fields.Integer()
    })
    flagged_item = api.model('flagged_item', {
        'span': fields.Nested(span),
        'type': fields.String(),
        'suggestions': fields.List(fields.String(256))
    })

class TestingDto:
    api = Namespace('testing', description='Contains all the testing-related operations')
    test_instance = api.model('test_instance', {
        'text': fields.String(256, description='The text which may contain errors.'),
        'flagged_spans': fields.List(fields.Nested(AnalysisDto.span))
    })
    test_set = api.model('test_set', {
        'test_instances': fields.List(fields.Nested(test_instance))
    })
    metric = api.model('metric', {
        'precision': fields.Float(),
        'recall': fields.Float(),
        'f1': fields.Float()
    })
    global_metrics = api.model('global_metrics', {
        'num_files': fields.Integer(),
        'metrics': fields.Nested(metric)
    })
