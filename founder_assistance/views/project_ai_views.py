"""
AI-powered views for project features.
This module serves as a central interface for all AI-related views.
"""

from .project_ai_chat_views import project_legal_chat
from .project_ai_content_views import project_content_generator
from .project_ai_analysis_views import (
    project_market_analysis,
    project_competitor_analysis
)
from .project_ai_customer_views import project_customer_research

__all__ = [
    'project_legal_chat',
    'project_content_generator',
    'project_market_analysis',
    'project_competitor_analysis',
    'project_customer_research',
]
