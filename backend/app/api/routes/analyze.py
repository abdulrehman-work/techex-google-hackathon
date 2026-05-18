from fastapi import APIRouter, HTTPException

from app.core.exceptions import BackendError, DataFetchError, TickerValidationError
from app.schemas.api import AnalyzeRequest, AnalyzeResponse
from app.services.analyze_workflow import AnalyzeWorkflow

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
    except BackendError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
