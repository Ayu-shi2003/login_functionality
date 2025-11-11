from sqlalchemy import Column,Integer,String,Boolean
from database import Base

class Users(Base):
    __tablename__ ="users"

    id = Column(Integer,primary_key=True,index=True)
    email= Column(String,unique=True,index=True)
    username = Column(String,unique=True,index=True)
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)

