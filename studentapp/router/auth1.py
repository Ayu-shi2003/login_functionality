from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from starlette import status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database1 import SessionLocal
from models1 import Users
from passlib.context import CryptContext

router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRETKEY='secretkey'
ALGORITHM='HS256'



def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')


class createUserRequest(BaseModel):
    username:str
    email:str
    role:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int,role:str,expires_deltatime:timedelta):
    encode={'sub':username,'id':user_id,'role':role}
    expires=datetime.utcnow()+expires_deltatime
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRETKEY,ALGORITHM)

async def current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token,SECRETKEY,algorithms=[ALGORITHM])
        username:str =payload.get("sub")
        user_id:int=payload.get("id")
        user_role:str=payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user.')
        return {'username':username,'id':user_id,'role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user.')


@router.post("/",status_code=status.HTTP_200_OK)
async def create_user(db:db_dependency,create_user:createUserRequest):
    create_user_model=Users(
        username = create_user.username,
        email=create_user.email,
        role=create_user.role,
        hashed_password= bcrypt_context.hash(create_user.password),
        is_active=True
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token",response_model=Token)
async def login_for_access_token(db:db_dependency,form_data:Annotated[OAuth2PasswordRequestForm,Depends()]):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=401,detail='invalid username or password')
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
    return Token(access_token=token,token_type='bearer')


