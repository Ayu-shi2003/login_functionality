from typing import Annotated
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models2
from database2 import engine, SessionLocal
from route import auth2,recipe

app = FastAPI()

models2.Base.metadata.create_all(bind=engine)

app.include_router(auth2.router)
app.include_router(recipe.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
