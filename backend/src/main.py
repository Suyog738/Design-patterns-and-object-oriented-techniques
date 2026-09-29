from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from interfaces.api.devices import router as devices_router
from infrastructure.settings import settings
from interfaces.api.health import router as health_router
from interfaces.api.sensors import router as sensors_router
from interfaces.api.locations import router as locations_router


app = FastAPI(
    title="Smart Greenhouse API",
    description="API for the Smart Greenhouse project",
    docs_url=None,
    redoc_url=None,
)


# CORS configuration
configured_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

allowed_origins = list(
    dict.fromkeys(
        configured_origins
        + [
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routers
app.include_router(health_router)
app.include_router(sensors_router)
app.include_router(devices_router)
app.include_router(locations_router)


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
