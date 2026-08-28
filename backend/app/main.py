from app.api.routes import router as reconciliation_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Finance Controller", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reconciliation_router)


@app.get("/")
def root():
    return {
        "service": "AI Finance Controller API",
        "status": "online",
        "docs": "/docs",
    }