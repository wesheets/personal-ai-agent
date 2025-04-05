from fastapi import APIRouter
import inspect
from fastapi.routing import APIRoute
from fastapi import FastAPI

router = APIRouter()

@router.get("/api/debug/routes")
async def list_routes(app_ref=None):
    if not app_ref:
        import app.main as main_module
        app_ref = getattr(main_module, "app", None)

    if not isinstance(app_ref, FastAPI):
        return {"error": "Invalid app reference or app not found."}

    routes_info = []
    for route in app_ref.routes:
        if isinstance(route, APIRoute):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods),
                "source": inspect.getsourcefile(route.endpoint)
            })
    return {"routes": routes_info}
