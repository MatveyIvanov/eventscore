import os

import uvicorn
from config.ecore import ecore

if __name__ == "__main__":
    ecore.discover_consumers()
    ecore.spawn_workers()
    uvicorn.run(
        "config:app",
        host="0.0.0.0",
        port=int(os.environ.get("ASGI_PORT", 8000)),
        reload=True,
    )
