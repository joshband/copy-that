"""
FastAPI routes for spacing token extraction.

This module contains API endpoints for:
- Single image extraction
- Batch extraction with aggregation
- SSE streaming for progress updates
"""

from .spacing_router import router

__all__ = [
    "router",
]
