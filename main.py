from typing import Annotated
from fastapi import FastAPI,Depends
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session  
import models
from database import engine,SessionLocal
from routers import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]