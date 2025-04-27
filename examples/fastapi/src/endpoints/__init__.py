from typing import Tuple

from endpoints.ping import router as ping_router
from fastapi.routing import APIRouter


def get_routers() -> Tuple[APIRouter, ...]:
    return (ping_router,)
