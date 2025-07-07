from fastapi import HTTPException

from langgraph.types import Command
from rich.pretty import pprint as rpprint

from api import app
from api import agent, compiled_graph

from tests.example_states import keywords_chosen_state

@app.post("/test/analyze/refine", summary="Refine Keywords")
async def test_refine_keywords(request):
    """
    Test endpoint to refine keywords using a predefined state.
    """
    try:
        config = {"configurable": {"thread_id": "1"}}

        # Simulate the refinement process using a predefined state
        resp = compiled_graph.invoke(keywords_chosen_state)
        graph_state = compiled_graph.get_state(config)
        rpprint(graph_state)

        return {
            "response": resp,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine keywords: {str(e)}")