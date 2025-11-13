from typing import Annotated
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,HTTPException,Path
from starlette import status
from models1 import Student
from database1 import SessionLocal
from .auth1 import current_user

router=APIRouter(
    prefix='/admin',
    tags=['admin']
)

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

@router.get("/student",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None or user.get('role') !='admin':
        raise HTTPException(status_code=401,detail='Authentication failed')
    return  db.query(Student).all()

@router.post("/",status_code=status.HTTP_200_OK)
async def create_Data(user:user_dependency,db:db_dependency,student_request:studentRequest):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')
    student_model=Student(**student_request.dict(),teacher_id=user.get('id'))
    db.add(student_model)
    db.commit()

@router.put("/student/{student_id}",status_code=status.HTTP_204_NO_CONTENT)
async def get_update(user:user_dependency,db:db_dependency,student_request:studentRequest,student_id:int=Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,detail='Authentication failed')
    student_model=db.query(Student).filter(Student.id==student_id).filter(Student.teacher_id==user.get('id')).first()
    if student_model is None:
        raise HTTPException(status_code=404,detail='student not found')
    
    student_model.name=student_request.name
    student_model.age=student_request.age
    student_model.grade=student_request.grade
    
    db.add(student_model)
    db.commit()

@router.delete("/{student_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(db:db_dependency,user:user_dependency,student_id:int=Path(gt=0)):
    if user is None or user.get('role')!= 'admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')
    student_model=db.query(Student).filter(Student.id==student_id).filter(Student.teacher_id==user.get('id')).first()
    if student_model is None:
        raise HTTPException(status_code=404,detail='student not found')
    
    db.query(Student).filter(Student.id==student_id).filter(Student.teacher_id==user.get('id')).delete()
    db.commit()