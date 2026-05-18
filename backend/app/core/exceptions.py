class BackendError(Exception):
    """Base backend error."""


class TickerValidationError(BackendError):
    """Raised when a ticker fails validation."""


class DataFetchError(BackendError):
    """Raised when upstream market data cannot be retrieved."""


class AiPipelineError(BackendError):
    """Raised when the AI agent pipeline cannot complete."""
