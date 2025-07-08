from fastapi import HTTPException
import uuid

from langgraph.types import Command
from rich.pretty import pprint as rpprint

from api import app
from api import AnalysisRequest, RankingsRequest
from api import compiled_graph

from geo_aval import DominanceGraph


@app.post("/analyze/get_keywords", summary="Start Analysis Session")
async def get_keywords(request: AnalysisRequest):
    """
    Start an analysis session and return session ID with selected keywords.
    This allows for interactive keyword managment before final results.
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        config = {"configurable": {"thread_id": session_id, "language": request.language, "location": request.city}}
        
        #(will stop after keywords were gathered)
        compiled_graph.invoke({
            "keywords": [],
            "target": request.brand_name,
            "graph": DominanceGraph(companies=[]),
            "messages": []
        }, config=config)

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
            config = {"configurable": {"thread_id": new_session_id, "language": language, "location": city}}
            compiled_graph.invoke({
                "keywords": keywords,
                "target": brand_name,
                "graph": DominanceGraph(companies=[]),
                "messages": []
            }, config=config)
        else:
            config = {"configurable": {"thread_id": session_id}}
            compiled_graph.invoke(Command(resume="", update={
                "keywords": keywords if len(keywords) > 0 else None
            }), config=config)

        values = compiled_graph.get_state(config).values

        graph = values.get("graph")
        return {
            "graph": graph,
        }        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine analysis: {str(e)}")
