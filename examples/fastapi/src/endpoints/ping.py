from config.ecore import ecore
from fastapi.routing import APIRouter

from eventscore.core.types import Event

router = APIRouter(prefix="/ping", tags=["ping"])


@router.get("/")
async def ping():
    ecore.produce(event=Event(type="ping", payload={"some": "value"}))
    return {"detail": "OK"}
