import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


class TextPreprocessor:

    @staticmethod
    def preprocess_text(text):
        tokens = TextPreprocessor.get_processed_tokens(text)
        processed_text = ' '.join(tokens)
        return processed_text

    @staticmethod
    def get_processed_tokens(text):
        text = text.lower()
        text = text.replace("\n", " ")
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in stop_words]
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        return tokens