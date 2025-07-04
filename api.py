from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import os
from dotenv import load_dotenv
from geo_aval import Agent
from langgraph.types import Command
from rich.pretty import pprint as rpprint
import json
from jsonpickle import dumps, loads

load_dotenv()

app = FastAPI(
    title="GEO Analysis API",
    description="🌍 GEO (Generative Engine Optimization) Evaluator - Analyze how your brand appears in AI responses",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AnalysisRequest(BaseModel):
    brand_name: str
    city: str
    language: Literal["pt_BR", "en_US"]

class CompanyResponse(BaseModel):
    name: str
    relevantUrls: List[str]
    times_cited: int

class RefineKeywordsRequest(BaseModel):
    session_id: str
    refined_keywords: List[str] = Field(..., description="Additional keywords to refine the analysis")

class AnalysisResponse(BaseModel):
    companies: List[CompanyResponse]
    keywords_used: List[str]
    location: str
    target: str
    status: str = "completed"

class ErrorResponse(BaseModel):
    error: str
    detail: str


agent = Agent()
compiled_graph = agent.get_graph()

@app.get("/", summary="API Health Check")
async def root():
    """Health check endpoint"""
    return {
        "message": "🌍 GEO Analysis API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/analyze/start", summary="Start Analysis Session")
async def start_analysis(request: AnalysisRequest):
    """
    Start an analysis session and return session ID for keyword refinement.
    This allows for interactive keyword refinement before final results.
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        
        config = {"configurable": {"thread_id": session_id}}
        
        #(will stop at keyword refinement)
        for chunk in agent.invoke(target=request.brand_name, city=request.city, language=request.language, config=config):
            rpprint(chunk)


        graph_state = compiled_graph.get_state(config)
        rpprint(graph_state)
        values = graph_state.values
        rpprint(values)
        refined_keywords = values.get("refined_keywords")
        
        return {
            "session_id": session_id,
            "keywords": refined_keywords,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.post("/stream/analyze/start", summary="Start Analysis Session")
async def start_analysis_stream(request: AnalysisRequest):
    """
    Start an analysis session and return session ID for keyword refinement.
    This allows for interactive keyword refinement before final results.
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
            for chunk in agent.invoke(target=request.brand_name, city=request.city, language=request.language, config=config):
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


@app.post("/analyze/refine", summary="Refine Keywords")
async def refine_keywords(request: RefineKeywordsRequest):
    """
    Add additional keywords to refine the analysis for a specific session.
    """
    try:
        session_id = request.session_id
        keywords = request.refined_keywords

        if (len(keywords) > 5):
            raise HTTPException(status_code=400, detail="You can only search for up to 5 keywords.")

        config = {"configurable": {"thread_id": session_id}}

        compiled_graph.invoke(Command(resume=""), config=config)
        
        values = compiled_graph.get_state(config).values
        graph = values.get("graph")

        return {
            "graph": graph,
        }        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine analysis: {str(e)}")


@app.post("/stream/analyze/refine", summary="Refine Keywords")
async def start_refine_keywords_stream(request: RefineKeywordsRequest):
    """
    Add additional keywords to refine the analysis for a specific session.
    This allows for interactive keyword refinement before final results.
    """
    async def generate_refine_keywords_stream():
        """
        Add additional keywords to refine the analysis for a specific session.
        """
        try:
            session_id = request.session_id
            keywords = request.refined_keywords

            if (len(keywords) > 5):
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




if __name__ == "__main__":
    import uvicorn
    
    # Check for API key
    if not os.getenv("GEO_AVAL_API_KEY"):
        print("❌ GEO_AVAL_API_KEY not found in environment variables!")
        print("Please add your OpenAI API key to the .env file")
        exit(1)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)