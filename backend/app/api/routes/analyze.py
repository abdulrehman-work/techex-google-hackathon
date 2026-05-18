from fastapi import APIRouter, HTTPException

from app.core.exceptions import AiPipelineError, BackendError, DataFetchError, TickerValidationError
from app.schemas.agent_context import AgentContextPayload
from app.schemas.api import AnalyzeRequest, AnalyzeResponse
from app.services.analyze_workflow import AnalyzeWorkflow
from app.services.ai_orchestrator import AiOrchestrator
from app.services.response_builder import ResponseBuilder

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_stock(payload: AnalyzeRequest) -> AnalyzeResponse:
    workflow = AnalyzeWorkflow()
    try:
        return workflow.run(payload.ticker)
    except TickerValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DataFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AiPipelineError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except BackendError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze/context", response_model=AnalyzeResponse)
def analyze_context(payload: AgentContextPayload) -> AnalyzeResponse:
    """Run the AI pipeline from an already-built structured context payload."""
    try:
        analysis = AiOrchestrator().run_agents(payload)
        return ResponseBuilder().build_frontend_response(
            context=payload,
            analysis=analysis,
            meta={"services": "provided-context,ai"},
        )
    except AiPipelineError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except BackendError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
