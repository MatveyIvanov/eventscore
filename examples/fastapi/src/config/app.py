import logging

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

import endpoints


__app = FastAPI(debug=True)
for router in endpoints.get_routers():
    __app.include_router(router, tags=router.tags)

__app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])



def get_fastapi_app() -> FastAPI:
    return __app

