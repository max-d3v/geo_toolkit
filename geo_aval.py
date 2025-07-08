import os
from dotenv import load_dotenv
from typing_extensions import TypedDict, Optional, Literal
from rich.console import Console

from langgraph.graph import MessagesState, StateGraph, END
from langchain_core.runnables import RunnableConfig

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import InMemorySaver

from pydantic import BaseModel, Field
from typing import List
from rich.pretty import pprint as rpprint

from prompts.en_US import (
    web_info_gathering_prompt,
    keywords_organization_prompt,
    refine_keywords_prompt,
    structure_brands_dominance_prompt,
    resume_target_info_prompt
)
from prompts.pt_BR import (
    web_info_gathering_prompt,
    keywords_organization_prompt,
    refine_keywords_prompt,
    structure_brands_dominance_prompt,
    resume_target_info_prompt
)


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

# Since tools will be different for different runtimes place them in config?
class ConfigSchema(TypedDict):
    tools: List[dict]
    language: Literal["pt_BR", "en_US"]
    location: str

class State(MessagesState):
    target: str
    keywords: List[str]
    graph: DominanceGraph | None

class Agent():
    def __init__(self):
        self.console = Console()
        
        builder = StateGraph(State, config_schema=ConfigSchema)
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
    
    @staticmethod
    def get_from_config(config: RunnableConfig, key: str):
        return config["configurable"].get(key, None)

    @staticmethod
    def add_city_to_keywords(keywords: List[str], city: str):
        """
        Adds the city to each keyword in the list.
        """
        return [f"{keyword} {city}" for keyword in keywords]
    
    @staticmethod
    def get_openai_web_research_tool(city: str):
        return {
            "type": "web_search_preview",
            "user_location": {
                "type": "approximate",
                "city": city,
                "region": city,
            }
        }

    @staticmethod
    def get_prompt(prompt: str, language: str):
        if language == "en_US":
            import prompts.en_US as en_prompts
            return getattr(en_prompts, prompt)
        else:
            import prompts.pt_BR as pt_prompts
            return getattr(pt_prompts, prompt)
        
    def starting_node(self, state: State):
        return { "messages": [] }

    def route_starting_node(self, state: State):
        keywords = state.get("keywords")
        if keywords and len(keywords) > 0:
            return "gather_results"
        else:
            return "web_research"


    def research_target(self, state: State, config: RunnableConfig):
        target = state.get("target")
        city = self.get_from_config(config, "location")
        language = self.get_from_config(config, "language")
        web_research_tool = self.get_openai_web_research_tool(city)


        web_researcher_agent = self.get_prompt(language=language, prompt="web_info_gathering_prompt") | llm.bind_tools([web_research_tool]) # The tool called directly in the openAI model runs automatically
        
        research_result = web_researcher_agent.invoke({"messages": [HumanMessage(content=target)]})

        return { "messages": [HumanMessage(target), research_result] }
    
    def get_keywords(self, state: State, config: RunnableConfig):
        messages = state.get("messages")
        language = self.get_from_config(config, "language")
        keyword_organizer_agent = self.get_prompt(prompt="keywords_organization_prompt", language=language) | smart_llm.with_structured_output(Keywords)
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
                
    def gather_cited_companies(self, state: State, config: RunnableConfig):
        keywords = state.get("keywords")
        language = self.get_from_config(config, "language")
        city = self.get_from_config(config, "location")
        web_research_tool = self.get_openai_web_research_tool(city)

        if keywords and len(keywords) == 0:
            raise Exception("No keywords given for gathering results.")
        if len(keywords) > 10:
            keywords = keywords[0:4]

        formatted_keywords = self.add_city_to_keywords(keywords, city)

        gathered_results = []
        for keyword in formatted_keywords:
            agent = ChatPromptTemplate([HumanMessage(keyword)]) | llm.bind_tools([web_research_tool])
            response = agent.invoke({})
            tool_called = response.additional_kwargs.get("tool_outputs")
            
            # Filter out responses that did not trigger web research
            if tool_called is not None and len(tool_called) > 0:
                structurer_agent = self.get_prompt(prompt="structure_brands_dominance_prompt", language=language) | llm.with_structured_output(DominanceGraph)
                for chunk in structurer_agent.stream({"web_results": [response]}):
                    
                    if isinstance(chunk, DominanceGraph) and chunk.companies:
                        companies = chunk.companies
                        gathered_results.append(companies)

        flattened_companies = [company for companies_list in gathered_results for company in companies_list]
        return { "graph": flattened_companies }

    


# Basically 2 types of entities to search - LOCAL OR GLOBAL. Global would be more aimed toward SaaSes or really global companies.