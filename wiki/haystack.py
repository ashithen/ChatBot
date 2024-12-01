from haystack.nodes import FARMReader
from haystack.schema import Document

class HaystackExtractor(object):

    def __init__(self):
        self.reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")

    def get_relevant_contexts(self, query, summaries, k=5):
        docs = [Document(content=summary) for summary in summaries]
        answers = self.reader.predict(query=query, documents=docs, top_k=k)
        all_contexts = [answer.context for answer in answers["answers"]]
        return " ".join(all_contexts)