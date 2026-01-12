import streamlit as st 
from langgraph_database_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

#***********************Utility function******************************************************

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
   thread_id= generate_thread_id()
   st.session_state['thread_id']=thread_id
   add_thread(st.session_state['thread_id'])
   
   st.session_state['message_history']=[]
   
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)   
        
# def load_chat(thread_id):
#     return chatbot.get_state(config={'configurable': {'thread_id':thread_id}} ).values['messages']       

def load_chat(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    messages = state.values.get("messages")

    if messages is None:
        # Old backend thread OR non-chat thread
        return []

    return messages

#**************** Session setup *********************************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()     
    
if 'chat_threads'not in st.session_state:
    st.session_state['chat_threads']=retrieve_all_threads();   
    
add_thread(st.session_state['thread_id'])    


    
    

# *****************Sidebar UI *****************************************************************
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages = load_chat(thread_id)
        
        temp_messages=[]
        
        for message in messages:
            if isinstance(message,HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            
            temp_messages.append({'role':role,'message':message.content})  # because the messages recieved from load_chat() were written in certain way , they are not compatible
        
        st.session_state['message_history']=temp_messages





# *******************************Main UI **************************************************************
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['message'])

# Message History format is : 
#[{'role':'user','content':'Hi'}] 
    
user_input=st.chat_input('Type here')    

if(user_input):
    
    thread_id=st.session_state['thread_id']
    
    st.session_state['message_history'].append({'role':'user','message':user_input})
     
    with st.chat_message('user'):
        st.text(user_input)
        
    #CONFIG= {'configurable': {'thread_id':st.session_state['thread_id']}}    
    
    #***************Now to get the chat  of same conversation in one place, you need to send metadata in which thread id of conversation in the config******************
    CONFIG={
        "configurable":{"thread_id":st.session_state['thread_id']},
        "metadata":{
            "thread_id":st.session_state["thread_id"]
        },
        "run_code":"chat_turn"
    }
         
    
    with st.chat_message('assistant'):
          
          ai_message=st.write_stream(
              message_chunk.content for message_chunk,metadata in chatbot.stream(
                  {'messages':[HumanMessage(content=user_input)]},
                  config=CONFIG,
                  stream_mode='messages'
              )
          )
          
    st.session_state['message_history'].append({'role':'assistant','message':ai_message})      