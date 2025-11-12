from datetime import datetime, timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from psutil import users
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from jose import ExpiredSignatureError, jwt,JWTError

router = APIRouter(
prefix="/auth",
tags=["auth"]
)

SECRET_KEY = "secretkey1"
ALGORITHM ="HS256"


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
  username:str
  email:str
  firstname:str
  lastname:str
  password:str
  role:str

class Token(BaseModel):
  access_token:str
  token_type:str

#class VerifyPasswordRequest(BaseModel):
 # plain_password:str
  #hashed_password:str

def get_db():
  db = SessionLocal()

  try:
     yield db
  finally:
    db.close()

db_dependency = Annotated[Session,Depends(get_db)]

def authenticate_user(username:str,password:str,db):
  user = db.query(Users).filter(Users.username == username).first()
  if not user:
    return False
  if not bcrypt_context.verify(password,user.hashed_password):
    return False
  return user

def create_access_token(username:str,user_id:int,role:str,expires_delta:timedelta):
  encode ={'sub':username,'id':user_id, 'role':role}
  expires=datetime.utcnow()+expires_delta
  encode.update({'exp':expires})
  return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
  try:
    payload =jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    username: str=payload.get('sub')
    user_id:int=payload.get('id')
    user_role:str=payload.get('role')
    if username is None or user_id is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user.')
    return {'username':username,'id':user_id,'role':user_role}
  except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired. Please log in again.'
        )
  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user.')
    


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request:CreateUserRequest,db:db_dependency):
  create_user_model=Users(
   email=create_user_request.email,
   username=create_user_request.username,
   firstname= create_user_request.firstname,
   lastname=create_user_request.lastname,
   role=create_user_request.role,
   hashed_password= bcrypt_context.hash(create_user_request.password),
   is_active=True
)
  db.add(create_user_model)
  db.commit()

#@router.post("/verifypassword")
#async def verify_password(verifyPassword:VerifyPasswordRequest):
 # password_verify=bcrypt_context.verify(verifyPassword.plain_password,verifyPassword.hashed_password)
  #if password_verify:
  #   return{"password is correct"}
  #else:
   #  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(user.username, user.id,user.role, timedelta(minutes=20))
    return Token(access_token=token, token_type="bearer")

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
  return {
        "message": f"Welcome {current_user['username']}!",
        "role": current_user['role']
    }
