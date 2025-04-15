"""
CRITIC Module Initialization

This module provides endpoints for evaluating agent outputs with reflection-aware
quality assessment and retry triggering for low-scoring outputs.
"""

from fastapi import APIRouter

# Import review router
from app.modules.critic.review import router as review_router

# Create main router
router = APIRouter()

# Include review router
router.include_router(review_router, tags=["critic"])
