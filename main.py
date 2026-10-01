from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models import Log
from llm import analyze_log

Base.metadata.create_all(bind=engine)
app = FastAPI(title="LogTriage")


class LogInput(BaseModel):
    content: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(input: LogInput, db: Session = Depends(get_db)):
    result = analyze_log(input.content)
    log = Log(
        content=input.content,
        severity=result["severity"],
        suggestion=result["suggestion"],
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {
        "id": log.id,
        "log": log.content,
        "severity": log.severity,
        "suggestion": log.suggestion,
        "created_at": log.created_at,
    }


@app.get("/logs")
def list_logs(limit: int = 20, db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.created_at.desc()).limit(limit).all()
    return logs


@app.get("/logs/{log_id}")
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


app.mount("/", StaticFiles(directory="static", html=True), name="static")