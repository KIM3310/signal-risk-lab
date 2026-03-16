from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.engine import execution_posture, factor_board, research_pack, risk_report, runtime_brief


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app = FastAPI(title="Signal Risk Lab", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "signal-risk-lab", "researchMode": True}


@app.get("/")
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/runtime/brief")
def runtime_brief_route() -> dict:
    return runtime_brief()


@app.get("/api/factor-board")
def factor_board_route() -> dict:
    return factor_board()


@app.get("/api/risk-report")
def risk_report_route() -> dict:
    return risk_report()


@app.get("/api/execution-posture")
def execution_posture_route() -> dict:
    return execution_posture()


@app.get("/api/research-pack")
def research_pack_route() -> dict:
    return research_pack()

