from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.messages import HumanMessage,BaseMessage
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import sqlite3


load_dotenv()

model = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"   
)


class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
def chat_node(state:ChatState):
    messages=state["messages"]
    response=model.invoke(messages)
    return {"messages":[response]} 
# sqlite3 works on same thread , so we tell it not to check , because we gonna use multiple threads of chats in it

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

#you need to create sqlite database behind and connect this checkpointer to sqlite database
checkpointer=SqliteSaver(conn=conn)    # connection object given by the database
    
    
graph=StateGraph(ChatState)
graph.add_node("chat_node",chat_node)
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)    

chatbot=graph.compile(checkpointer=checkpointer)

# Here we need to define somethings for the frontend that , how many  threads are there present in the backend, so that we can get them
def retrieve_all_threads():
  all_threads= set()
  for checkpoint in checkpointer.list(None):
    all_threads.add(checkpoint.config['configurable']['thread_id'])
    
  return(list(all_threads))



    