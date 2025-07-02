import os
from dotenv import load_dotenv
from typing_extensions import Annotated, TypedDict

from langgraph.graph import MessagesState, StateGraph, END

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from pydantic import BaseModel, Field
from typing import List
from rich.pretty import pprint as rpprint

# Import prompts based on language preference
from prompts.pt_BR import (
    web_info_gathering_prompt,
    keywords_organization_prompt,
    refine_keywords_prompt,
    structure_brands_dominance_prompt,
    resume_target_info_prompt
)

# from prompts.en_US import (
#     web_info_gathering_prompt,
#    keywords_organization_prompt,
#     refine_keywords_prompt,
#     structure_brands_dominance_prompt
# )


load_dotenv()


# LLM initialization 
dumbass_llm = ChatOpenAI(model="gpt-4.1-nano", api_key=os.getenv("GEO_AVAL_API_KEY"))
llm = ChatOpenAI(model="gpt-4.1-mini", api_key=os.getenv("GEO_AVAL_API_KEY"))
smart_llm = ChatOpenAI(model="gpt-4.1", api_key=os.getenv("GEO_AVAL_API_KEY"))

# Tools
class Company(BaseModel):
    "Company data"
    name: str
    relevantUrls: List[str] = Field(description="All the URLs given for this brand, EXCEPT google maps, do not add google maps URLs here.")
    times_cited: int

class DominanceGraph(BaseModel):
    "List of companies cited"
    companies: List[Company]

class Keywords(TypedDict):
    keywords: List[str] = Field(description="List of the keywords abstracted from given info")

web_openai_research_tool= {"type": "web_search_preview", "user_location": {
    "type": "approximate",
    "country": "BR",
    "city": "Joinville",
    "region": "Joinville",
}}


# Agent definition

class State(MessagesState):
    target: str
    location: str | None
    all_keywords: Keywords
    refined_keywords: Keywords
    graph: DominanceGraph

class Agent():
    def __init__(self):
        builder = StateGraph(State)
        builder.add_node("web_research", self.research_target)
        builder.add_node("get_keywords", self.get_keywords)
        builder.add_node("refine_keywords", self.refine_keywords)
        builder.add_node('gather_results', self.gather_cited_companies)

        builder.set_entry_point("web_research")
        builder.add_edge("web_research", "get_keywords")
        builder.add_edge("get_keywords", "refine_keywords")
        builder.add_edge("refine_keywords", "gather_results")
        builder.add_edge("gather_results", END)

        self.graph = builder.compile()

    def invoke(self, target: str, location: str):
        self.graph.invoke({
            "keywords": [],
            "target": target,
            "location": location
        })

    def research_target(self, state: State):
        print("=== Generating company overview ===")

        target = state.get("target")
        location = state.get("location")
        web_researcher_agent = web_info_gathering_prompt | llm.bind_tools([web_openai_research_tool]) # The tool called directly in the openAI model runs automatically
        research_result = web_researcher_agent.invoke({"messages": [HumanMessage(content=target)]})

        rpprint(research_result)
        return { "messages": [HumanMessage(target), research_result], "location": location }
    
    def get_keywords(self, state: State):
        print("=== Generating Keywords ===")

        messages = state.get("messages")
        keyword_organizer_agent = keywords_organization_prompt | smart_llm.with_structured_output(Keywords)
        keywords = []
        last_length = 1
        for chunk in keyword_organizer_agent.stream({"messages": messages}):
            if 'keywords' in chunk and chunk['keywords']:
                new_length = len(chunk["keywords"])
                if new_length > last_length:
                    keyword = chunk["keywords"][-2]
                    print(f"Keyword found: {keyword}")
                    keywords.append(keyword)
                    last_length = new_length
        
        return { "all_keywords": keywords }

    def refine_keywords(self, state: State):
        print("=== Refining keywords ===")

        keywords = state.get("all_keywords")
        location = state.get("location")
        messages = state.get("messages")

        target_resume = (resume_target_info_prompt | dumbass_llm).invoke({"messages": messages})


        agent = refine_keywords_prompt | smart_llm.with_structured_output(Keywords)
        response = agent.invoke({"keywords": keywords, "target_resume": target_resume})
        
        refined_keywords = []
        for keyword in response["keywords"]:
            refined_keywords.append(f"{keyword} {location or ""}")

        print(refined_keywords)
        return { "refined_keywords": refined_keywords }
        
    def gather_cited_companies(self, state: State):
        print("=== Gathering and organizing cited companies ===")

        keywords = state.get("refined_keywords")
        if len(keywords) > 5:
            keywords = keywords[0, 4]


        researches_results = []
        for keyword in keywords:
            agent = ChatPromptTemplate([HumanMessage(keyword)]) | llm.bind_tools([web_openai_research_tool]) # The keywords should be structured in a way that triggers a web research. If none is triggered, will base it in the llms base of knowledge
            response = agent.invoke({})
            researches_results.append(response)
        
        
        structurer_agent = structure_brands_dominance_prompt | llm.with_structured_output(DominanceGraph)
        structurer_response = structurer_agent.invoke({"web_results": researches_results})

        rpprint(structurer_response.companies)
        return { "graph": structurer_response.companies }
        
            




# Basically 2 types of entities to search - LOCAL OR GLOBAL. Global would be more aimed toward SaaSes or really global companies. 

agent = Agent()
agent.invoke("Copapel", "Joinville")
