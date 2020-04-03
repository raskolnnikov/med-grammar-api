
import uuid
import datetime
import numpy as np
import pandas as pd
import joblib
from spacy.tokenizer import Tokenizer
from flask import current_app
import re
from collections import Counter
from collections import defaultdict
import docx2txt
import os
from symspellpy import SymSpell, Verbosity
import glob
import logging

from ..model.grammar_objects import Span, N_Tuple, Sentence, Text_Object, Flagged_Item

def analyze_text(data):
    txt = data['text']
    doc = current_app.nlp(txt)
    text_obj = Text_Object(doc)
    flagged_spans, flagged_reasons, suggestions = find_words_out_of_context(text_obj, current_app.trigram_counter, current_app.spell_checker)

    if not txt:
        response_object = {
            'status': 'fail',
            'message': 'There was an error analyzing the text. Please try again.'
        }
        return response_object, 409
    response_object = [
            Flagged_Item(
                s.__dict__,
                flagged_reasons[i],
                suggestions[i]
            )
            for i, s in enumerate(flagged_spans)
        ]
    return response_object, 200

def check_spelling(data):
    txt = data['text'].lower()
    return get_spelling_suggestion(txt, current_app.spell_checker)

def get_triples(data):
    txt = data['text'].lower()
    trigrams = [t for t in current_app.trigram_counter if txt in t]
    return trigrams



def find_suspect_trigrams(sentence, trigram_counter):
    tg = sentence.get_n_tuples(3)
    suspects = []
    for t in tg:
        if not is_trigram_known(t.text_tuple, trigram_counter):
            suspects.append(t)
    return suspects

def find_suspect_word(trigram_list):
    candidate_suspects = []
    f = defaultdict(int)

    for t in trigram_list:
        for span in t.tuple:
            if '-' not in span.text:
                f[span] += 1
                if span.dist_from_first < 3:
                    f[span] += 1
                    if span.dist_from_first == 0:
                        f[span] += 1
                elif span.dist_from_last < 3:
                    f[span] += 1
                    if span.dist_from_last == 0:
                        f[span] += 1
    keys = np.array(list(f.keys()))
    values = np.array(list(f.values()))
    if not len(values):
        max_count = 0
    else:
        max_count = max(values)
    idx = np.argwhere(values>=2).flatten()
    max_count_spans = np.array([w for w in keys[idx] if not excluded(w)])
    return max_count_spans

# Exclude some words from being considered suspect, e.g.: stop words such as 'if', 'of', 'and'
def excluded(w):
    return (len(w.text)==3 and is_stopword(w.text.lower())
        or len(w.text)<3)

def has_stopword_majority(trigram):
    return sum([is_stopword(w) for w in trigram if len(w) < 4]) > 1

def is_stopword(word):
    return word in current_app.nlp.Defaults.stop_words

def get_spelling_suggestion(w, spell_checker):
    try:
        max_edit_distance_lookup = 3
        suggestion_verbosity = Verbosity.ALL  # TOP, CLOSEST, ALL
        suggestions = spell_checker.lookup(w, suggestion_verbosity,
                                       max_edit_distance_lookup)
        return [s.term for s in suggestions[:8] if not words_share_lemma(s.term.lower(), w.lower())]
    except Exception as e:
        print(e)
        return ['no_suggestions']

def words_share_lemma(w1, w2):
    w1_lemma = current_app.nlp(w1)[0].lemma
    w2_lemma = current_app.nlp(w2)[0].lemma

    return w1_lemma == w2_lemma

def get_word_trigrams(span, trigrams):
    word_trigrams = []
    for t in trigrams:
        if span in t.tuple:
            word_trigrams.append(t)
    return word_trigrams

def replace_in_list(l, a, b):
    new_l = []
    for x in l:
        if x == a:
            new_l.append(b)
        else:
            new_l.append(x)
    return tuple(new_l)

def is_trigram_known(t, counter):
    return t in counter

def find_words_out_of_context(text_object, trigram_counter, spell_checker):
    logging.basicConfig(
        filename=current_app.config['UPLOADED_PATH']+"logfile.log",
        level=logging.INFO,
        filemode='w'

    )

    sentences = []
    candidates = []
    unknowns = []
    for sentence in text_object.sents:
        logging.info("xxxxxxxxxxxxxxxxxxx")
        logging.info("-------------------")

        suspect_trigrams = find_suspect_trigrams(sentence, trigram_counter)
        logging.info("suspect trigrams = ")
        for t in suspect_trigrams:
            logging.info("\t"+str(t))

        suspects = find_suspect_word(suspect_trigrams)
        logging.info("suspects = ")
        for s in suspects:
            logging.info("\t"+str(s))

        scores = np.zeros(len(suspects))
        suspect_data_log = defaultdict(dict)
        for i, span in enumerate(suspects):
            suspect_data_log[span] = {
                'span_suspect_trigrams': [],
                'span_trigram_frequency_score': 0,
                'span_score': 0
            }

            word_trigrams = get_word_trigrams(span, suspect_trigrams)
            suggestions = get_spelling_suggestion(span.text, spell_checker)
            for t in word_trigrams:
                trigram_data_log = {
                    'trigram': t.text_tuple,
                    'valid_trigram_suggestions': [],
                }
                for s in suggestions:
                    new_trigram = replace_in_list(t.text_tuple, span.text.lower(), s.lower())
                    if is_trigram_known(new_trigram, trigram_counter):
                        tg_freq = current_app.trigram_counter[new_trigram]
                        trigram_suggestion_data_log = {
                                                        'trigram': new_trigram,
                                                        'freq': tg_freq,
                                                        'stopword_majority_flag': False,
                                                        'flipped_stopword_flag': False,
                                                        'boundary_span_flag': False
                        }
                        if not is_stopword(span.text.lower()):
                            suspect_data_log[span]['span_trigram_frequency_score'] += tg_freq

                            if span.dist_from_first == 0 or span.dist_from_last == 0:
                                scores[i] += 2
                                suspect_data_log[span]['span_score'] += 2
                                trigram_suggestion_data_log['boundary_span_flag'] = True
                            elif span.dist_from_first == 1 or span.dist_from_last == 1:
                                scores[i] += 0.5
                                suspect_data_log[span]['span_score'] += 0.5
                                trigram_suggestion_data_log['boundary_span_flag'] = True
                            if not has_stopword_majority(new_trigram):
                                    scores[i] += 1
                                    suspect_data_log[span]['span_score'] += 1
                            else:
                                    scores[i] += 0.5
                                    suspect_data_log[span]['span_score'] += 0.5
                            trigram_data_log['valid_trigram_suggestions'].append(trigram_suggestion_data_log)



                suspect_data_log[span]['span_suspect_trigrams'].append(trigram_data_log)
        log_suspect_data(suspect_data_log, logging)
        style_candidates = []
        flagged_units = {}
        for u in set(flagged_units.items()):
            style_candidates.append(u)
        candidates += list([ (c,'semantically_suspect') for c in suspects[np.argwhere(scores>1)].flatten()])
        unknowns += [(s, 'unknown_word_in_context_vocabulary') for s in suspects[np.argwhere(scores==0)].flatten() if s.text.lower() not in current_app.dictionary]
        logging.info("-------------------")
        logging.info("xxxxxxxxxxxxxxxxxxx")

    flagged = candidates+unknowns
    flagged_spans = []
    flagged_reasons = []
    suggested_corrections = []

    for i, c in enumerate(flagged):
        flagged_spans.append(c[0])
        flagged_reasons.append(c[1])
        suggested_corrections.append(get_spelling_suggestion(c[0].text, spell_checker)[:3])

    return flagged_spans, flagged_reasons, suggested_corrections

def log_suspect_data(data, logger):
        from pprint import pformat
        for span in data.keys():
            logger.info('*********************')
            logger.info('SPAN = %s' %(str(span)))
            logger.info('SPAN TRIPLE FREQUENCY SCORE = %i' %(data[span]['span_trigram_frequency_score']))
            logger.info('SPAN TOTAL SCORE = %i' %(data[span]['span_score']))
            logger.info('SPAN SUSPECT TRIGRAMS')
            for t in data[span]['span_suspect_trigrams']:
                logger.info('\tTRIGRAM = %s' %(str(t['trigram'])))
                for vt in t['valid_trigram_suggestions']:
                    logger.info('\t\tNEW TRIGRAM = %s' %(str(vt['trigram'])))
                    logger.info('\t\t\tFREQUENCY = %s' %(str(vt['freq'])))
                    logger.info('\t\t\tSTOPWORD MAJ FLAG = %s' %(str(vt['stopword_majority_flag'])))
                    logger.info('\t\t\tFIPPED STOPWORD FLAG = %s' %(str(vt['flipped_stopword_flag'])))
                    logger.info('\t\t\tBOUNDARY SPAN FLAG = %s' %(str(vt['boundary_span_flag'])))
            logger.info('__*****************__')

def find_trigrams_with_words(word_list):
    for t in trigram_counter:
        if any([w for w in word_list if w in t]):
            print(t)

def generate_highlighted_markup(text_obj, flagged_spans):
    text = text_obj.text
    for i, span in enumerate(reversed(flagged_spans)):
        print(span.text, "-",span.start_idx,"-",span.end_idx)
        text = text[:span.start_idx]+'<mark class="g-bg-primary h3 g-color-white" data-toggle="tooltip" data-placement="bottom" title="title">&nbsp'+span.text+'&nbsp;<span class="u-label g-bg-blue">'+str(len(flagged_spans)-i)+'</span></mark>'+text[span.end_idx:]
    return text

def get_global_metrics(result_list):
    global_tp = 0
    global_fp = 0
    global_fn = 0
    for r in result_list:
        global_tp += r['counts']['tp']
        global_fp += r['counts']['fp']
        global_fn += r['counts']['fn']

    precision, recall, f1 = get_precision_recall_f1(global_tp, global_fp, global_fn)
    return {
        'num_files': len(result_list),
        'metrics': {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    }

def get_precision_recall_f1(tp, fp, fn):
    try:
        precision = tp / (tp + fp)
    except Exception as e:
        precision = 1
    try:
        recall = tp / (tp + fn)
    except Exception as e:
        recall = 1
    try:
        f1 = 2*(precision * recall / (precision + recall))
    except Exception as e:
        f1 = 0

    return precision, recall, f1
