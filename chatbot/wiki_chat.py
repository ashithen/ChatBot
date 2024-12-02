import vertexai
from vertexai.generative_models import GenerativeModel

from wiki.haystack import HaystackExtractor
from wiki.indexer import WikiIndexer


class WikiChat(object):

    PROJECT_ID = "irproject1-436619"
    vertexai.init(project=PROJECT_ID, location="us-central1")

    prompt_template = """
    Extract relevant texts for the given query from the following context and give the consice summary of it.
    Just give the consice summary, don't add any error messages or the information about the context.
    
    Query : 
    {query}
    Context : 
    {context}
    """

    def __init__(self):
        self.indexer = WikiIndexer()
        self.extractor = HaystackExtractor()
        self.model = GenerativeModel("gemini-1.5-flash-002")

    def getResponseFromWiki(self, query, summaries):
        # extracted_text = self.extractor.get_relevant_contexts(query, summaries)
        return self.get_summary(query, '\n'.join(summaries))

    def get_summary(self, query, summaries):
        prompt = self.prompt_template.format(query=query,context=summaries)
        summary = self.model.generate_content(prompt).text
        return summary
