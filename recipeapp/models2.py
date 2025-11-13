from database2 import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Boolean

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

class Recipes(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    ingredients = Column(String)
    make_time = Column(String) 
    difficulty = Column(String)
    is_public = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Grocery(Base):
    __tablename__ = "grocery"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    items = Column(String) 
    created_by = Column(Integer, ForeignKey("users.id"))
