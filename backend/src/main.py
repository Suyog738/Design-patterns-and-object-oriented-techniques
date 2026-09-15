from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from infrastructure.settings import settings
from interfaces.api.health import router as health_router
from interfaces.api.sensors import router as sensors_router


app = FastAPI(
    title="Smart Greenhouse API",
    description="API for the Smart Greenhouse project",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(sensors_router)


@app.get("/")
def root():
    return {
        "project": "Smart Greenhouse",
        "message": "Smart Greenhouse API",
        "scalar": "/scalar",
        "openapi": "/openapi.json",
    }


@app.get("/scalar", include_in_schema=False)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Smart Greenhouse API",
    )