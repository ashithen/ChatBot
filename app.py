from flask import Flask, jsonify
from flask import request
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
    user_id = data['user_id']
    return jsonify(api_handler.get_response(user_id, query, topics))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
