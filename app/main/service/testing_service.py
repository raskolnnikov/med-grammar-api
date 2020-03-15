from ..service.analysis_service import find_words_out_of_context, get_global_metrics, get_precision_recall_f1
from ..model.grammar_objects import Span, Text_Object
from flask import current_app

def test_logic(text, true_flagged_spans, trigram_counter, spell_checker):
    print("start test from file")
    doc = current_app.nlp(text)
    text_obj = Text_Object(doc)
    predicted_flagged_spans, _, _  = find_words_out_of_context(text_obj, trigram_counter, spell_checker)
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    fp_list = []
    fn_list = []

    print('true flagged')
    for span in true_flagged_spans:
        print("text = %s, %i - %i" %(span.text, span.start_idx, span.end_idx))
        if span in predicted_flagged_spans:
            tp += 1
        else:
            fn += 1
            fn_list.append(span)

    print('predicted flagged')
    for span in predicted_flagged_spans:
        print("text = %s, %i - %i" %(span.text, span.start_idx, span.end_idx))

        if span not in true_flagged_spans:
            fp += 1
            fp_list.append(span)

    precision, recall, f1 = get_precision_recall_f1(tp, fp, fn)

    print("done test from file")
    return {
        'metrics':{
            'precision': precision,
            'recall': recall,
            'f1': f1
        },
        'spans':{
            'fp':fp_list,
            'fn':fn_list
        },
        'counts':{
            'tp':tp,
            'fp':fp,
            'fn':fn
        },
        'text': text_obj.text
    }

def test_logic_api(test_set):
    results = []
    for instance in test_set['test_instances']:
        text = instance['text']
        flagged_spans = instance['flagged_spans']
        span_list = []

        for fs in flagged_spans:
            span_list.append(
                Span(fs['text'], fs['start_idx']-1, fs['end_idx']-1)
            )
        print(span_list)
        results.append(
            test_logic(
                text,
                span_list,
                current_app.trigram_counter,
                current_app.spell_checker
            )
        )
    global_metrics = get_global_metrics(results)
    return global_metrics

def parse_test_instance(path):
    flagged_spans = []
    with open(path, 'r+', encoding="utf8") as input_file:
        for i,line in enumerate(input_file):
            if i == 0:
                text = line.replace('\n','').replace('\r','')
            else:
                values = line.split('\t')
                try:
                    span = Span(values[0], int(values[1])-1, int(values[2])-1)
                    flagged_spans.append(span)
                except Exception as e:
                    print(e)
    return text,flagged_spans
