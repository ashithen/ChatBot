from rank_bm25 import BM25Okapi
import json

import app
from util.text_preprocessing import TextPreprocessor
from util.filereader import get_absolute_path


class WikiIndexer(object):

    def __init__(self):
        self.bm25 = BM25Okapi(self.get_tokenized_doc())
        self.wiki_docs = self.get_all_docs()

    def get_all_docs(self):
        with open(get_absolute_path('wiki_docs.json'),'r') as f:
            all_docs = json.load(f)
        return all_docs
    def get_tokenized_doc(self):
        with open(get_absolute_path('tokenized_docs.json'),'r') as f:
            t_docs = json.load(f)
        return t_docs

    def get_top_docs(self, query, topics, k=5):
        query = TextPreprocessor.preprocess_text(query)
        scores = self.bm25.get_scores(query)
        score_doc_list = list(zip(scores, self.wiki_docs))
        score_doc_list = sorted(score_doc_list, key=lambda x: x[0], reverse=True)
        # filtered_docs = [d['summary'] for _,d in score_doc_list if d['topic'] in topics]
        filtered_docs = [sd for sd in score_doc_list if sd[1]['topic'] in topics]
        return filtered_docs[:k]
