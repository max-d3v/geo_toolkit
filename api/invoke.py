from fastapi import HTTPException
import uuid

from langgraph.types import Command
from rich.pretty import pprint as rpprint

from api import app
from api import AnalysisRequest, RankingsRequest
from api import agent, compiled_graph



@app.post("/analyze/get_keywords", summary="Start Analysis Session")
async def get_keywords(request: AnalysisRequest):
    """
    Start an analysis session and return session ID with selected keywords.
    This allows for interactive keyword managment before final results.
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        
        config = {"configurable": {"thread_id": session_id}}
        
        #(will stop after keywords were gathered)
        agent.invoke(target=request.brand_name, city=request.city, language=request.language, config=config)

        graph_state = compiled_graph.get_state(config)
        values = graph_state.values
        keywords = values.get("keywords")

        return {
            "session_id": session_id,
            "keywords": keywords,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@app.post("/analyze/get_rankings", summary="Refine Keywords")
async def get_rankings(request: RankingsRequest):
    """
    Gather rankings based on chosen keywords.
    """
    try:
        session_id = request.session_id
        keywords = request.keywords
        language = request.language
        city = request.city
        brand_name = request.brand_name

        if (len(keywords) > 10):
            raise HTTPException(status_code=400, detail="You can only search for up to 5 keywords.")

        if session_id is None:
            new_session_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": new_session_id}}
            agent.invoke(brand_name, city, language, keywords, type="invoke", config=config)
            values = compiled_graph.get_state(config).values
        else:
            config = {"configurable": {"thread_id": session_id}}
            compiled_graph.invoke(Command(resume=""), config=config)
            values = compiled_graph.get_state(config).values
        

        graph = values.get("graph")
        return {
            "graph": graph,
        }        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine analysis: {str(e)}")
