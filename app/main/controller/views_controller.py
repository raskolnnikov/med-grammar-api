from flask import request, render_template
import glob
from flask import Blueprint, current_app
from ..model.grammar_objects import Span, Text_Object
from ..service.analysis_service import find_words_out_of_context, generate_highlighted_markup, get_global_metrics
from ..service.testing_service import parse_test_instance, test_logic
import os
import docx2txt

bp = Blueprint('views', __name__)
colors = ['red', 'green', 'blue', 'yellow', 'orange', 'gray', 'beige', 'purple']

@bp.route('/analyze', methods=('GET', 'POST'))
def analyze():
    if request.method == 'POST':
        if request.form['text-block'] != '':
            text = request.form['text-block']
        else:
            files = glob.glob(current_app.config['UPLOADED_PATH']+"/*.docx")
            files.sort(key=os.path.getmtime, reverse=True)
            text = docx2txt.process(files[0]).replace('\n\n\n\n\n\n\n\n', ' ')

        doc = current_app.nlp(text)
        text_obj = Text_Object(doc)
        flagged_spans, flagged_reasons, suggestions = find_words_out_of_context(text_obj, current_app.trigram_counter, current_app.spell_checker)
        highlighted_text = generate_highlighted_markup(text_obj, flagged_spans)
        print("text = "+highlighted_text)
        return render_template('text/index.html', highlighted_text=highlighted_text, colors=colors, called=True, c=len(flagged_spans), flagged_spans=flagged_spans, flagged_reasons=flagged_reasons, suggestions=suggestions)

    else:
        return render_template('text/index.html', called=False, c=0)

@bp.route('/test', methods=('GET', 'POST'))
def test():
    if request.method == 'POST':
        files = glob.glob(current_app.config['UPLOADED_PATH']+"/test*.txt")
        files.sort(key=os.path.getmtime, reverse=True)
        print(files)
        results = []
        for f in files:
            text, span_list = parse_test_instance(f)
            results.append(test_logic(text, span_list, current_app.trigram_counter, current_app.spell_checker))
            os.remove(f)
        global_metrics = get_global_metrics(results)
        return render_template('text/test.html', called=True, results=results, global_metrics=global_metrics, files=files )

    else:
        return render_template('text/test.html', called=False, c=0)

@bp.route('/upload', methods=['POST'])
def upload():
    for key, f in request.files.items():
        if key.startswith('file'):
            f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
    return '', 204
