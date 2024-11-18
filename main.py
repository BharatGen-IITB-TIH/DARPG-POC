from typing import Union
from graph import make_workflow
from fastapi import FastAPI, Body
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
from typing import Annotated
from langchain_core.messages import RemoveMessage
from pymongo import MongoClient
from mongo_db import MongoDBSaver
import os

app = FastAPI()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "key.json"

client = MongoClient(host="173.17.0.6", port=27017)
memory = MongoDBSaver(client=client, db_name="darpg-db-prod")
workflow = make_workflow()
lg_app = workflow.compile(checkpointer=memory)

class query(BaseModel):
    input: str
    session_id: str

@app.post("/chat/")
async def chat(user_query: query):
    config = {"configurable": {"thread_id": user_query.session_id}}
    res = lg_app.invoke({"input_msg": user_query.input}, config)

    return {"response": res["messages"][-1].content}