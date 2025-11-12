from typing import Annotated
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,HTTPException,Path
from starlette import status
from database1 import SessionLocal
from models1 import Student
from .auth1 import current_user

router=APIRouter()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(current_user)]

class studentRequest(BaseModel):
    name:str
    age:int 
    grade:str

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    
    return db.query(Student).filter(Student.teacher_id==user.get('id')).all()

@router.get("/students/{student_id}",status_code=status.HTTP_200_OK)
async def read_student(user:user_dependency,db:db_dependency,student_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    
    student_model=db.query(Student).filter(Student.id==student_id).filter(Student.teacher_id==user.get('id')).first()
    if student_model is not None:
        return student_model
    raise HTTPException(status_code=404,detail='student not found')

@router.post("/student",status_code=status.HTTP_201_CREATED)
async def create_student(db:db_dependency,student_request:studentRequest,user:user_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    student_model=Student(**student_request.dict(),teacher_id=user.get('id'))
    db.add(student_model)
    db.commit()