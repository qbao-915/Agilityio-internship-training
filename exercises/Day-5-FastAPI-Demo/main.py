from fastapi import FastAPI
from routers.hello import router as hello_router
from routers.items import router as items_router

app = FastAPI()

# Include routers
app.include_router(hello_router)
app.include_router(items_router)