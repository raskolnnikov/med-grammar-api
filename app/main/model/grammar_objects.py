class Flagged_Item:
    def __init__(self, span, type, suggestions):
        self.span = span
        self.type = type
        self.suggestions = suggestions

class Text_Object:
    def __init__(self, doc):
        self.text = doc.text
        self.sents = self.init_sents(doc)

    def init_sents(self, doc):
        sents = [Sentence(sent) for sent in doc.sents]
        return sents

class Sentence:
    def __init__(self, sent):
        self.spans = self.init_spans(sent)
        self.text = ' '.join([s.text for s in self.spans])

    def init_spans(self, sent):
        sent_len = sent.__len__()
        sent_spans = []
        for t in sent:
            if not t.is_punct and not t.is_space and t.is_alpha:
                dist_from_first = self.dist_from_first(t.i, sent)
                dist_from_last = self.dist_from_last(t.i, sent)
                sent_spans.append(Span(t.text, t.idx, t.idx + len(t), dist_from_first, dist_from_last))
        return sent_spans

    def get_n_tuples(self, n):
        span_tuples = tuple(zip(*[self.spans[i:] for i in range(n)]))
        return [N_Tuple(t) for t in span_tuples]

    def dist_from_first(self, i, sent):
        return sum([1 for t in sent if t.i < i and t.is_alpha])

    def dist_from_last(self, i, sent):
        return sum([1 for t in sent if t.i > i and t.is_alpha])

class N_Tuple:
    def __init__(self, span_tuple):
        self.tuple = span_tuple
        self.text_tuple = self.get_text_tuple(span_tuple)

    def get_text_tuple(self, span_tuple):
        return tuple([t.text.lower() for t in span_tuple])

    def __str__(self):
        return "<"+str(self.text_tuple)+">"


class Span():
    def __init__(self, text, start_idx, end_idx, dist_from_first=-1, dist_from_last=-1):
        self.text = text
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.dist_from_first = dist_from_first
        self.dist_from_last = dist_from_last

    def __eq__(self, other):
        return (self.text == other.text and
                self.start_idx == other.start_idx and
                self.end_idx == other.end_idx)

    def __hash__(self):
        return hash(self.text+str(self.start_idx)+str(self.end_idx))

    def is_boundary(self):
        return not self.dist_from_first or not self.dist_from_last

    def __str__(self):
        return "<text: %s, start_idx: %i, end_idx: %i, dist_from_first: %i, dist_from_last: %i>" % (self.text, self.start_idx, self.end_idx, self.dist_from_first, self.dist_from_last)
