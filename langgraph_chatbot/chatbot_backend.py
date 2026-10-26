from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
import operator
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()
model = ChatGroq(model="openai/gpt-oss-20b")
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
def chat_node(state: ChatState):
    messages = state['messages']

    response = model.invoke(messages)

    return {'messages': response}
checkpointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node', END)
chatbot = graph.compile(checkpointer=checkpointer)
chatbot

initial_state = {
    'messages': HumanMessage(content='What is the capital of India?')
}

chatbot.invoke(initial_state)['messages'][1].content
thread_id='1'


while True:
    user_message = input('Type here: ')
    print('user: ', user_message)
    if user_message.strip().lower() in ['exit', 'quit', 'bye']:
        break

    config = {'configurable': {'thread_id': thread_id}}

    response = chatbot.invoke({'messages': HumanMessage(content=user_message)}, config=config)

    print('AI: ', response['messages'][-1].content)


