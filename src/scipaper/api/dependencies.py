"""API dependencies for authentication."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

security = HTTPBearer()

async def api_key_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """API key authentication dependency."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    api_key = credentials.credentials
    if api_key != "your-api-key-here":  # Replace with actual key or from settings
        logger.warning(f"Invalid API key attempted: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"API key authenticated for request")
    return api_key