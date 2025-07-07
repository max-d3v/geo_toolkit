import sys
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field, model_validator
from typing import List, Literal, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from geo_aval import Agent

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

class RankingsRequest(BaseModel):
    session_id: Optional[str]
    brand_name: Optional[str]
    city: Optional[str]
    language: Optional[Literal["pt_BR", "en_US"]]
    keywords: Optional[List[str]]

    @model_validator(mode="after")
    def validade_ranking_request(self):
        if self.session_id is not None:
            return self
        elif all([self.brand_name, self.city, self.language]):
            return self
        else:
            raise ValueError("Either session_id or brand_name, city, and language must be provided.")

    @model_validator(mode="after")
    def validate_keywords_length(self):
        if self.keywords and len(self.keywords) > 10:
            raise ValueError("You can only search for up to 10 keywords.")
        return self


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

import invoke 
import streaming


@app.get("/", summary="API Health Check")
async def root():
    """Health check endpoint"""
    return {
        "message": "🌍 GEO Analysis API is running",
        "status": "healthy",
        "version": "1.0.0"
    }



