from fastapi import APIRouter, Depends
from app.api.files.routes import router as files_router
from app.api.auth.security import get_current_user

router = APIRouter()

# Include files router with authentication middleware
router.include_router(
    files_router,
    prefix="/files",
    tags=["files"],
    dependencies=[Depends(get_current_user)]
)
