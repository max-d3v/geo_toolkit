from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from langgraph.types import Command
from rich.pretty import pprint as rpprint
from jsonpickle import dumps

from api import app
from api import AnalysisRequest, RankingsRequest
from api import compiled_graph

from ..geo_aval import DominanceGraph

@app.post("/stream/analyze/get_keywords", summary="Start Analysis Session")
async def start_analysis_stream(request: AnalysisRequest):
    """
    Start an analysis session and return session ID with selected keywords.
    This allows for interactive keyword managment before final results.
    """
    async def generate_analysis_stream():
        try:
            import uuid
            session_id = str(uuid.uuid4())
            
            
            config = {"configurable": {"thread_id": session_id}, "language": request.language, "location": request.city}

            yield dumps({
                "stage": "initializing",
                "session_id": session_id,
                "data": None
            }, unpicklable=False) + "\n"
            
            #(will stop at keyword refinement)  
            for chunk in compiled_graph.stream({
                "keywords": [],
                "target": request.brand_name,
                "graph": DominanceGraph(companies=[]),
                "messages": []
            }, config=config):
                yield dumps({
                    "stage": "analysys",
                    "session_id": session_id,
                    "data": chunk
                }, unpicklable=False) + "\n"
            
            graph_state = compiled_graph.get_state(config)
            values = graph_state.values
            keywords = values.get("keywords")
            
            yield dumps({
                "stage": "completed",
                "session_id": session_id,
                "data": {
                    "keywords": keywords,
                }
            }, unpicklable=False) + "\n"
        except Exception as e:
            yield dumps({
                "stage": "error",
                "session_id": session_id if 'session_id' in locals() else None,
                "data": f"Failed to start analysis: {str(e)}",
            }, unpicklable=False) + "\n"

    return StreamingResponse(
        generate_analysis_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@app.post("/stream/analyze/get_rankings", summary="Refine Keywords")
async def start_refine_keywords_stream(request: RankingsRequest):
    """
    Gather rankings based on chosen keywords.
    """
    async def generate_refine_keywords_stream():
        try:
            session_id = request.session_id
            keywords = request.keywords
            language = request.language
            city = request.city
            brand_name = request.brand_name

            if keywords and len(keywords) > 10:
                raise HTTPException(status_code=400, detail="You can only search for up to 10 keywords.")

            yield dumps({
                "stage": "initializing",
                "session_id": session_id,
                "data": None
            }, unpicklable=False) + "\n"

            if session_id is None:
                import uuid
                new_session_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": new_session_id, "language": language, "location": city}}
                
                for chunk in compiled_graph.stream({
                    "keywords": keywords,
                    "target": brand_name,
                    "graph": DominanceGraph(companies=[]),
                    "messages": []
                }, config=config):
                    yield dumps({
                        "stage": "gathering_results",
                        "session_id": new_session_id,
                        "data": chunk
                    }, unpicklable=False) + "\n"
                
                values = compiled_graph.get_state(config).values
                session_id = new_session_id
            else:
                config = {"configurable": {"thread_id": session_id}}
                
                for chunk in compiled_graph.stream(Command(resume="", update={"keywords": keywords if len(keywords) > 0 else None}), config=config):
                    yield dumps({
                        "stage": "gathering_results",
                        "session_id": session_id,
                        "data": chunk
                    }, unpicklable=False) + "\n"
                
                values = compiled_graph.get_state(config).values
            
            graph = values.get("graph")

            yield dumps({
                "stage": "completed",
                "session_id": session_id,
                "data": {
                    "graph": graph,
                }
            }, unpicklable=False) + "\n"   
        except Exception as e:
            rpprint(e)
            yield dumps({
                "stage": "error",
                "session_id": session_id if 'session_id' in locals() else None,
                "data": f"Failed to refine analysis: {str(e)}",
            }, unpicklable=False) + "\n"
    
    return StreamingResponse(
        generate_refine_keywords_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )