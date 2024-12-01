from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os
from chatbot.api_handlers import ChatBotHandler


app = Flask(__name__)
api_handler = ChatBotHandler()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/ask', methods=['POST'])
def get_response():
    data = request.get_json()
    query = data['query']
    topics = data['topics'] if 'topics' in data else []
    return api_handler.get_response(query, topics)





if __name__ == '__main__':
    app.run()
