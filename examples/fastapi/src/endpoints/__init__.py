from typing import Tuple

from fastapi.routing import APIRouter

from endpoints.ping import router as ping_router
from endpoints.pong import router as pong_router


def get_routers() -> Tuple[APIRouter, ...]:
    return (ping_router, pong_router)

