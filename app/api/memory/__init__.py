from fastapi import APIRouter, Depends
from app.api.memory.routes import router as memory_router
from app.api.auth.security import get_current_user

router = APIRouter()

# Include memory router with authentication middleware
router.include_router(
    memory_router,
    prefix="/memory",
    tags=["memory"],
    dependencies=[Depends(get_current_user)]
)
