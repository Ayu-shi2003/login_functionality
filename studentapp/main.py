from typing import Annotated
from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
import models1
from database1 import engine,SessionLocal
from router import auth1,students1


app = FastAPI()

models1.Base.metadata.create_all(bind=engine)

app.include_router(auth1.router)
app.include_router(students1.router)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]