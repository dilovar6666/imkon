from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routers import admin, applications, auth, employers, resumes, users, vacancies

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", openapi_url="/api/v1/openapi.json", docs_url="/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in (auth.router, users.router, employers.router, resumes.router, vacancies.router, applications.router, admin.router):
    app.include_router(router, prefix="/api/v1")


@app.get("/openapi.json", include_in_schema=False)
def root_openapi() -> JSONResponse:
    return JSONResponse(app.openapi())


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
