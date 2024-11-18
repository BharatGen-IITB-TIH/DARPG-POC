import gradio as gr
import random
from graph import make_workflow
from langchain_core.messages import RemoveMessage
from langgraph.checkpoint.memory import MemorySaver
import aiofiles
import asyncio
from mongo_db import MongoDBSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from pymongo import MongoClient
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "key.json"

client = MongoClient("mongodb://173.17.0.6:27017/")
memory = MongoDBSaver(client=client, db_name="darpg-abhay")
# memory = MemorySaver()
workflow = make_workflow()
lg_app = workflow.compile(checkpointer=memory)


sessions = {}
ids = set()

def same_auth(username, password):
    user = username

    if user in sessions.keys():
        print("User already exist !!")
    
    else:
        config_id = random.randint(1, 1000)
        
        while(config_id in ids):
            config_id = random.randint(1, 1000)

        sessions[user] = config_id
        ids.add(config_id)
        
        with open("user_ids.txt", "a") as file:
            file.write(f"{user} ----> {config_id}\n")

        print("User created !!")

    return username == password


def chatbot_response(user_input, history, request: gr.Request):

    if request:
        user = request.username

    config_id = sessions[user]
    
    response = ""
   
    config = {"configurable": {"thread_id": config_id}}

    event = lg_app.invoke({"input_msg": user_input}, config)
    # print(event)

    response = event['messages'][-1].content


    return response

def clear_chat_history(request:gr.Request):

    if request:
        user = request.username

    config_id = sessions[user]
    config = {"configurable": {"thread_id": config_id}}

    memory.delete(config=config)

    while(config_id in ids):
        config_id = random.randint(1, 1000)

    sessions[user] = config_id
    ids.add(config_id)

    print("Clearing chat history")


with gr.ChatInterface(
        fn=chatbot_response,
        title="DARPG",
        description="Your darpg chatbot",
        clear_btn=gr.ClearButton(value="🗑️ Clear")
    ) as iface:
    iface.clear_btn.click(fn=clear_chat_history)

iface.launch(auth=same_auth, server_port=7860)