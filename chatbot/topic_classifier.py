import pickle

from sklearn.pipeline import Pipeline

from util.filereader import get_absolute_path
from util.text_preprocessing import TextPreprocessor


class TopicClassifier:

    def get_saved_model(self) -> Pipeline:
        with open(get_absolute_path('topic_classifier.pkl'),'rb') as file:
            loaded_model = pickle.load(file)
        return loaded_model

    def __init__(self):
        self.topic_model = self.get_saved_model()

    def classify(self, query):
        query_p = TextPreprocessor.preprocess_text(query)
        return self.topic_model.predict([query_p])[0]
