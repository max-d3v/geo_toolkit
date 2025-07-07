from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from langgraph.types import Command
from rich.pretty import pprint as rpprint
from jsonpickle import dumps

from api import app
from api import AnalysisRequest, CompanyResponse, RankingsRequest, AnalysisResponse, ErrorResponse
from api import agent, compiled_graph

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
            
            
            config = {"configurable": {"thread_id": session_id}}

            yield dumps({
                "stage": "initializing",
                "session_id": session_id,
                "data": None
            }, unpicklable=False) + "\n"
            
            #(will stop at keyword refinement)
            for chunk in agent.invoke(target=request.brand_name, city=request.city, language=request.language,  config=config):
                yield dumps({
                    "stage": "analysys",
                    "session_id": session_id,
                    "data": chunk
                }, unpicklable=False) + "\n"
            
            graph_state = compiled_graph.get_state(config)
            values = graph_state.values
            rpprint(values)
            refined_keywords = values.get("refined_keywords")
            
            yield dumps({
                "stage": "completed",
                "session_id": session_id,
                "data": {
                    "keywords": refined_keywords,
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
            keywords = request.refined_keywords

            if (len(keywords) > 10):
                raise HTTPException(status_code=400, detail="You can only search for up to 5 keywords.")

            config = {"configurable": {"thread_id": session_id}}

            yield dumps({
                "stage": "initializing",
                "session_id": session_id,
                "data": None
            }, unpicklable=False) + "\n"

            for chunk in compiled_graph.stream(Command(resume=""), config=config):
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



