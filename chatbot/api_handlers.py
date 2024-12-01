from chatbot.chitchat import ChitChat
from chatbot.topic_classifier import TopicClassifier
from chatbot.wiki_chat import WikiChat
from wiki.indexer import WikiIndexer
from  chatbot.chat_response import ChatResponse


class ChatBotHandler:

    def __init__(self):
        self.chitchat = ChitChat()
        self.topic_classifier = TopicClassifier()
        self.wiki_chat = WikiChat()
        self.wiki_indexer = WikiIndexer()

    def get_response(self, user_id, query, topics):
        topics = [t.lower() for t in topics]

        if self.chitchat.isChitChat(query):
            chat_response = self.chitchat.chat(user_id, query)
            response = ChatResponse(user_id=user_id, query=query,
                                    query_type="chitchat",topics=topics,response=chat_response)
            return response
        else:
            if len(topics) == 0:
                topics = [self.topic_classifier.classify(query)]
            top_score_docs = self.wiki_indexer.get_top_docs(query, topics)
            summaries = [d['summary'] for _,d in top_score_docs]
            response_text = self.wiki_chat.getResponseFromWiki(query, summaries)
            doc_scores = [(s,d['title']) for s,d in top_score_docs]
            response = ChatResponse(user_id=user_id, query=query, query_type="wiki",
                                    topics=topics, doc_scores=doc_scores, response=response_text)
            return response
