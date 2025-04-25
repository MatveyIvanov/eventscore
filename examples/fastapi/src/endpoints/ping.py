from eventscore.core.types import Event
from fastapi import BackgroundTasks, Depends, Header, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.routing import APIRouter

from config.ecore import ecore
router = APIRouter(prefix="/ping", tags=["ping"])


@router.get("/")
async def ping():
    ecore.produce(event=Event(type="ping", payload={"some": "value"}))
    return {"detail": "OK"}

