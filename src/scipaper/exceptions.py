"""Centralized exception definitions for SciPaper."""


class SciPaperError(Exception):
    """Base exception for all SciPaper errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def is_transient(self) -> bool:
        """Check if this error is transient (suitable for retry)."""
        return False


class SourceError(SciPaperError):
    """Exception raised when a data source encounters an error."""


class ParseError(SciPaperError):
    """Exception raised when parsing fails."""


class ConfigurationError(SciPaperError):
    """Exception raised when configuration is invalid."""


class ValidationError(SciPaperError):
    """Exception raised when data validation fails."""


class NetworkError(SciPaperError):
    """Exception raised when network operations fail."""

    def is_transient(self) -> bool:
        return True

    def is_transient(self) -> bool:
        return True


class AuthenticationError(SciPaperError):
    """Exception raised when authentication fails."""

    def is_transient(self) -> bool:
        return False

    def is_transient(self) -> bool:
        return False


class RateLimitError(SciPaperError):
    """Exception raised when API rate limits are exceeded."""

    def is_transient(self) -> bool:
        return True

    def is_transient(self) -> bool:
        return True


class AgentError(SciPaperError):
    """Exception raised when AI agent operations fail."""

    def is_transient(self) -> bool:
        return True

    def is_transient(self) -> bool:
        return True


class FetcherError(SciPaperError):
    """Exception raised when the fetcher encounters an error."""

    def is_transient(self) -> bool:
        return False
