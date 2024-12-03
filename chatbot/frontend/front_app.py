import streamlit as st
import seaborn as sns
import requests
import shelve
import uuid
from collections import Counter
from nltk.corpus import stopwords
import nltk
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

nltk.download("stopwords")
STOPWORDS = set(stopwords.words("english"))


user_emoji = "👤"
bot_emoji = "🤖"


TOPICS = [
    "Health", "Environment", "Technology", "Economy",
    "Entertainment", "Sports", "Politics", "Education",
    "Travel", "Food"
]

def generate_user_id():
    return str(uuid.uuid4())


if "user_id" not in st.session_state:
    st.session_state.user_id = generate_user_id()

def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages, max_conversations=100):
    with shelve.open("chat_history") as db:
        db["messages"] = messages[-max_conversations:]  


if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()


with st.sidebar:
    selected_page = st.radio("Navigate", ["Chat", "Analyze"])
    
    
    st.subheader("Topics")
    selected_topics = []
    for topic in TOPICS:
        if st.checkbox(topic, value=False, key=f"checkbox_{topic}"):  
            selected_topics.append(topic)

    if st.button("Delete Chat History"):
        st.session_state.messages = []
        st.session_state.user_id = generate_user_id()
        st.info(f"Chat history cleared. New User ID: {st.session_state.user_id}")



if selected_page == "Chat":
    st.markdown("""
                <style>
                .center-text {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    text-align: center;
                }
                </style>
            """, unsafe_allow_html=True)
    st.markdown('<div class="center-text"><h3>Chat Interface</h3></div>', unsafe_allow_html=True)
    st.write(f"User ID: {st.session_state.user_id}")
    
    for message in st.session_state.messages:
        avatar = user_emoji if message["role"] == "user" else bot_emoji
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


    if prompt := st.chat_input("Hello"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        

        with st.chat_message("user", avatar=user_emoji):
            st.markdown(prompt)


        api_url = "http://35.226.231.106:5000/ask"
        payload = {
            "query": prompt,
            "topics": selected_topics,
            "user_id": st.session_state.user_id
        }
        try:
            with st.spinner("Processing..."):
                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                api_response = response.json()
            
            bot_reply = api_response.get("response", "No response")
            query_type = api_response.get("query_type", "unknown")
            doc_scores = api_response.get("doc_scores")
            topics = api_response.get("topics", [])

            if not bot_reply:
                bot_reply = "Sorry, I wasn't able to find anything about the question you asked."

            
            st.session_state.messages.append({
                "role": "assistant",
                "query": prompt,
                "content": bot_reply,
                "query_type": query_type,
                "doc_scores": doc_scores,
                "topics": topics,
            })

            save_chat_history(st.session_state.messages,50)
                
            with st.chat_message("assistant", avatar=bot_emoji):
                st.markdown(bot_reply)
        
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 500:
                with st.chat_message("assistant", avatar=bot_emoji):
                    st.markdown("Sorry, there was an issue with the server. Please try again later.")
            else:
                with st.chat_message("assistant", avatar=bot_emoji):
                    st.markdown(f"Sorry, an HTTP error as occurred : {http_err} \nPlease try again later.")
        except requests.exceptions.RequestException as err:
            with st.chat_message("assistant", avatar=bot_emoji):
                st.markdown(f"Sorr, An error has occurred: {err}\nPlease try again later.")
        except Exception as e:
            with st.chat_message("assistant", avatar=bot_emoji):
                st.markdown(f"An unexpected error occurred: {str(e)}\nPlease try again later.")




# Analyze Page
elif selected_page == "Analyze":
    st.subheader("Chat Analysis")
    messages = load_chat_history()
    if not messages:
        st.write("No chat history available for analysis.")
    else:
        query_type_toggle = st.radio("Select Query Type for Analysis", ["chitchat", "wiki"])

        if query_type_toggle == "wiki":
            wiki_messages = [
                msg for msg in messages if msg.get("query_type") == "wiki"
            ]
            last_10_wiki_messages = wiki_messages[-10:]
            
            if last_10_wiki_messages:
                st.subheader("Wiki Queries Analysis")
                queries_and_topics = []
                for i in range(len(last_10_wiki_messages)):
                    queries_and_topics.append({
                        "Query Index": i + 1,  
                        "Query": last_10_wiki_messages[i]["query"],
                        "Topic": ', '.join(last_10_wiki_messages[i]["topics"])  
                    })

                df = pd.DataFrame(queries_and_topics)

                html = "<table style='width:100%; border-collapse: collapse; text-align: center;'>"
                html += "<tr><th>Query Index</th><th>Query</th><th>Topic</th></tr>"

                for _, row in df.iterrows():
                    html += f"<tr><td>{row['Query Index']}</td><td>{row['Query']}</td><td>{row['Topic']}</td></tr>"

                html += "</table>"

                st.markdown(html, unsafe_allow_html=True)
                

                st.subheader("Topic Distribution of the Last 10 Wiki Queries")
                last_10_topics = [msg.get("topics", []) for msg in last_10_wiki_messages]

                topic_counts = Counter([topic for sublist in last_10_topics for topic in sublist])
                if topic_counts:
                    st.write(f"Topic distribution in the last 10 queries: {dict(topic_counts)}")

                    fig, ax = plt.subplots(figsize=(7, 7))  
                    ax.pie(topic_counts.values(), labels=topic_counts.keys(), autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')  
                    st.pyplot(fig)

                st.subheader("Comparison of all the Unique Documents Across Last 10 Queries")
                if len(last_10_wiki_messages) > 1:
                    top_docs = {}
                    for msg in last_10_wiki_messages:
                        if msg.get("doc_scores"):
                            for score, doc in msg["doc_scores"]:
                                top_docs[doc] = top_docs.get(doc, 0) + score

                    
                    sorted_docs = sorted(top_docs.items(), key=lambda x: x[1], reverse=True)
                    doc_names = [doc for doc, _ in sorted_docs]
                    doc_scores = [score for _, score in sorted_docs]

                    
                    st.write(f"Total {len(top_docs)} unique docs out of {len(last_10_wiki_messages)*5}")
                    comparison_df = pd.DataFrame({"Document": doc_names, "Total Score": doc_scores})
                    st.bar_chart(comparison_df.set_index("Document"))


                st.subheader("Common Words in Wiki Responses (Excluding Stopwords)")
                wiki_responses = " ".join([msg["content"] for msg in last_10_wiki_messages])
                word_counts = Counter(
                    word for word in wiki_responses.split() if word.lower() not in STOPWORDS
                )
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_counts)
                st.image(wordcloud.to_array())


                st.subheader("Document Relevance Heat Map")
                doc_scores_data = []
                documents = set()  
                queries = [] 
                
                for msg in last_10_wiki_messages:
                    if msg.get("doc_scores"):
                        queries.append(msg["query"])
                        for score, doc in msg["doc_scores"]:
                            documents.add(doc)  
                            doc_scores_data.append([msg["query"], doc, score])

                df_scores = pd.DataFrame(doc_scores_data, columns=["Query", "Document", "Score"])
                heatmap_data = df_scores.pivot_table(index="Query", columns="Document", values="Score", fill_value=0)
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", cbar=True, linewidths=0.5, ax=ax)
                ax.set_title("Document Relevance Heat Map")
                st.pyplot(fig)

            else:
                st.write("No Wiki queries available.")
        
        elif query_type_toggle == "chitchat":
            chitchat_messages = [
                msg for msg in messages if msg.get("query_type") == "chitchat"
            ]
            if chitchat_messages:
                st.subheader("Chitchat Queries")
                for i, msg in enumerate(chitchat_messages, start=1):
                    st.write(f"{i}. Chitchat Query: {msg['query']}")

                st.subheader("Common Words in Chitchat Responses (Excluding Stopwords)")
                chitchat_responses = " ".join(
                    [msg["content"] for msg in chitchat_messages]
                )
                word_counts = Counter(
                    word for word in chitchat_responses.split() if word.lower() not in STOPWORDS
                )
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_counts)
                st.image(wordcloud.to_array())

            else:
                st.write("No Chitchat queries available.")
