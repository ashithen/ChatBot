import pickle

from transformers import AutoModelForCausalLM, AutoTokenizer

from util.filereader import get_absolute_path
from util.text_preprocessing import TextPreprocessor


class ChitChat(object):

    def load_chitchat_classifier(self):
        with open(get_absolute_path('chitchat_classifier.pkl'),'rb') as file:
            loaded_model = pickle.load(file)
        return loaded_model

    def __init__(self):
        self.chitchat_classifier = self.load_chitchat_classifier()
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.chitchat_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

    def isChitChat(self, message):
        message = TextPreprocessor.preprocess_text(message)
        res = self.chitchat_classifier.predict([message])[0]
        return res == "chitchat"

    def chat(self, used_id: str, query: str):
        input_ids = self.tokenizer.encode(query + self.tokenizer.eos_token, return_tensors="pt")
        chat_history_ids = self.chitchat_model.generate(input_ids, max_length=1000,
                                                        pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0],
                                     skip_special_tokens=True)
