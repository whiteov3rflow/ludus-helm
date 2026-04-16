"""FastAPI application entry point."""
from fastapi import FastAPI

app = FastAPI(
    title="insec-platform",
    description="Training lab deployment management for insec.ml",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
