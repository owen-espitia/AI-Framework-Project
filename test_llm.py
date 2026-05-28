# import requests

# user_message = """
#             How do shoes relate to politics?
# """
# response = requests.post(
#     "http://localhost:11434/api/chat",
#     json={
#         "model": "ai/gemma4:latest",
#         "messages": [{"role": "system", "content": """You are a helpful customer service bot for a shoe store called SoleMates. 
#                     Only answer questions about shoes, shoe care, sizing, and orders. Do not answer questions about any other topic
#                     """},
#                     {"role": "user", "content": user_message}]
#     }
# )
# bot_response = response.json()["choices"][0]["message"]["content"]
# print(bot_response)
import ollama

response = ollama.chat(
    model="llama3.1",
    messages=[
        {'role': 'system', 'content': 'You are a single celled amoeba, trying your hardest to survive in a microscopic version of New York. You have a heavy New York attitude and talk like the Notorious BIG.'},
        {'role': 'user', 'content': 'How has your day been?'},
    ]
)
print(response['message']['content'])