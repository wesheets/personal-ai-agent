from fastapi import APIRouter, Depends
from app.api.agents.routes import router as agents_router
from app.api.auth.security import get_current_user

router = APIRouter()

# Include agents router with authentication middleware
router.include_router(
    agents_router,
    prefix="/agents",
    tags=["agents"],
    dependencies=[Depends(get_current_user)]
)
