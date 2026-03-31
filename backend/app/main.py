from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .api import keywords, filters, results, sources, settings, integrations, historical

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Mention Monitor API",
    version="2.0.0",
    description="Система мониторинга и парсинга упоминаний из социальных сетей, мессенджеров и веб-сайтов",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(keywords.router, prefix="/api/keywords", tags=["keywords"])
app.include_router(filters.router, prefix="/api/filters", tags=["filters"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(historical.router, prefix="/api/historical", tags=["historical"])


@app.get("/")
def read_root():
    return {"message": "Mention Monitor API v2.0 is running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
