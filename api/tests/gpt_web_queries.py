import os
from dotenv import load_dotenv

from langgraph.graph import MessagesState, StateGraph, END

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from rich.pretty import pprint as rpprint
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", output_version="responses/v1", api_key=os.getenv("GEO_AVAL_API_KEY")).bind_tools([{"type": "web_search_preview", "user_location": {
    "type": "approximate",
    "country": "BR",
    "city": "Joinville",
    "region": "Joinville",
}}], strict=True)

agent = ChatPromptTemplate([HumanMessage("procure produtos de limpeza industrial")]) | llm
resp = agent.invoke({})
rpprint(resp)
