from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..deps import require_user, require_admin
from ..docker_manager import get_status, start_container, stop_container, get_logs


router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request, _=Depends(require_user)):
    status = get_status()
    return templates.TemplateResponse("dashboard.html", {"request": request, "status": status})


@router.post("/start")
def start(_=Depends(require_admin)):
    start_container()
    return RedirectResponse(url="/", status_code=303)


@router.post("/stop")
def stop(_=Depends(require_admin)):
    stop_container()
    return RedirectResponse(url="/", status_code=303)


@router.get("/logs")
def logs(request: Request, _=Depends(require_user)):
    content = get_logs()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": content})

