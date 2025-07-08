import os
from dotenv import load_dotenv
from typing_extensions import Annotated, TypedDict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from langgraph.graph import MessagesState, StateGraph, END

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import InMemorySaver

from pydantic import BaseModel, Field
from typing import List
from rich.pretty import pprint as rpprint



load_dotenv()

# LLM initialization 

dumbass_llm = ChatOpenAI(model="gpt-4.1-nano", api_key=os.getenv("GEO_AVAL_API_KEY"))
llm = ChatOpenAI(model="gpt-4.1-mini", api_key=os.getenv("GEO_AVAL_API_KEY"))
smart_llm = ChatOpenAI(model="gpt-4.1", api_key=os.getenv("GEO_AVAL_API_KEY"))

# Structured Outputs

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

# Agent definition

class State(MessagesState):
    target: str
    location: str
    keywords: List[str]
    graph: DominanceGraph | None

class Agent():
    def __init__(self):
        self.console = Console()
        
        builder = StateGraph(State)
        builder.add_node("starting_node", self.starting_node)
        builder.add_node("web_research", self.research_target)
        builder.add_node("get_keywords", self.get_keywords)
        builder.add_node('gather_results', self.gather_cited_companies)

        builder.set_entry_point("starting_node")
        builder.add_conditional_edges("starting_node", self.route_starting_node)
        builder.add_edge("web_research", "get_keywords")
        builder.add_edge("get_keywords", "gather_results")
        builder.add_edge("gather_results", END)
        

        checkpointer = InMemorySaver()
        self.graph = builder.compile(checkpointer=checkpointer, interrupt_after=["get_keywords"])

    def get_graph(self):
        return self.graph

    def invoke(self, target: str, city: str, language: str, keywords: List[str], type: str, stream_type: Optional[str] = None, config: dict | None = None):
        self.language = language

        if language == "en_US":
            from prompts.en_US import (
                web_info_gathering_prompt,
                keywords_organization_prompt,
                refine_keywords_prompt,
                structure_brands_dominance_prompt,
                resume_target_info_prompt
            )
        else:
            from prompts.pt_BR import (
                web_info_gathering_prompt,
                keywords_organization_prompt,
                refine_keywords_prompt,
                structure_brands_dominance_prompt,
                resume_target_info_prompt
            )

        self.web_info_gathering_prompt = web_info_gathering_prompt
        self.keywords_organization_prompt = keywords_organization_prompt
        self.refine_keywords_prompt = refine_keywords_prompt
        self.structure_brands_dominance_prompt = structure_brands_dominance_prompt
        self.resume_target_info_prompt = resume_target_info_prompt
        
        self.openai_web_research_tool = {"type": "web_search_preview", "user_location": {
            "type": "approximate",
            "city": city,
            "region": city,
        }}

        if type == "invoke":
            # This is the initial invocation, we will start the research
            return self.graph.invoke({
                "keywords": keywords,
                "target": target,
                "location": city,
                "graph": DominanceGraph(companies=[]),
                "messages": []
            }, config)
        else:
            return self.graph.stream({
                "keywords": keywords,
                "target": target,
                "location": city,
                "graph": DominanceGraph(companies=[]),
                "messages": []
            }, stream_mode=stream_type, config=config)
        
    def starting_node(self, state: State):
        return { "messages": [] }

    def route_starting_node(self, state: State):
        keywords = state.get("keywords")
        if keywords and len(keywords) > 0:
            return "gather_results"
        else:
            return "web_research"


    def research_target(self, state: State):
        target = state.get("target")
        location = state.get("location")
        web_researcher_agent = self.web_info_gathering_prompt | llm.bind_tools([self.openai_web_research_tool]) # The tool called directly in the openAI model runs automatically
        research_result = web_researcher_agent.invoke({"messages": [HumanMessage(content=target)]})

        return { "messages": [HumanMessage(target), research_result], "location": location }
    
    def get_keywords(self, state: State):
        messages = state.get("messages")
        keyword_organizer_agent = self.keywords_organization_prompt | smart_llm.with_structured_output(Keywords)
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
        
        return { "keywords": keywords }
    
    @staticmethod
    def add_city_to_keywords(keywords: List[str], city: str):
        """
        Adds the city to each keyword in the list.
        """
        return [f"{keyword} {city}" for keyword in keywords]

    
            
    def gather_cited_companies(self, state: State):
        keywords = state.get("keywords")
        if keywords and len(keywords) == 0:
            raise Exception("No keywords given for gathering results.")
        if len(keywords) > 10:
            keywords = keywords[0:4]

        formatted_keywords = self.add_city_to_keywords(keywords, state.get("location"))

        gathered_results = []
        for keyword in formatted_keywords:
            agent = ChatPromptTemplate([HumanMessage(keyword)]) | llm.bind_tools([self.openai_web_research_tool])
            response = agent.invoke({})
            tool_called = response.additional_kwargs.get("tool_outputs")
            
            # Filter out responses that did not trigger web research
            if tool_called is not None and len(tool_called) > 0:
                structurer_agent = self.structure_brands_dominance_prompt | llm.with_structured_output(DominanceGraph)
                for chunk in structurer_agent.stream({"web_results": [response]}):
                    
                    if isinstance(chunk, DominanceGraph) and chunk.companies:
                        companies = chunk.companies
                        gathered_results.append(companies)

        flattened_companies = [company for companies_list in gathered_results for company in companies_list]
        return { "graph": flattened_companies }

    
        

# Basically 2 types of entities to search - LOCAL OR GLOBAL. Global would be more aimed toward SaaSes or really global companies.