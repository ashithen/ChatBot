from wiki.haystack import HaystackExtractor
from wiki.indexer import WikiIndexer
from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel

class WikiChat(object):

    prompt_template = """
    Write a concise summary of the following text.

    ```{text}```

    SUMMARY:
    """

    def __init__(self):
        self.indexer = WikiIndexer()
        self.extractor = HaystackExtractor()
        aiplatform.init(project='irproject1-436619', location='us-central1')
        self.generation_model = TextGenerationModel.from_pretrained("text-bison@002")

    def getResponseFromWiki(self, query, summaries):
        extracted_text = self.extractor.get_relevant_contexts(query, summaries)
        return self.get_summary(extracted_text)

    def get_summary(self, text):
        prompt = self.prompt_template.format(text=text)
        summary = self.generation_model.predict(prompt=prompt, max_output_tokens=256).text
        return summary
