from typing import Annotated, List
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,HTTPException,Path
from starlette import status
from database2 import SessionLocal
from models2 import Recipes
from .auth2 import current_user

router=APIRouter(
    prefix='/Recipes',
    tags=['Recipes']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(current_user)]

class RecipeRequest(BaseModel):
    name: str
    description: str
    ingredients: str
    make_time: str
    difficulty: str
    is_public: bool = False
    views:bool

class RecipeDisplay(BaseModel):
    id: int
    name: str
    description: str
    ingredients: str
    make_time: str
    difficulty: str
    is_public: bool
    views: int
    created_by: int

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    
    return db.query(Recipes).filter(Recipes.owner_id==user.get('id')).all()


@router.get("/{recipe_id}",status_code=status.HTTP_200_OK)
async def get_recipe(user:user_dependency,db:db_dependency,recipe_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication failed')
    user_model= db.query(Recipes).filter(Recipes.id==recipe_id).filter(Recipes.owner_id==user.get('id')).first()
    if user_model is not None:
       return user_model
    raise HTTPException(status_code=404,detail='recipe not found')


@router.get("/public/all")
async def get_public_recipes(db: db_dependency):
    recipes = db.query(Recipes).filter(Recipes.is_public == True).all()
    return recipes

@router.get("/users/")
async def get_users_recipes(db: db_dependency,user:user_dependency):
    recipes = db.query(Recipes).filter(Recipes.owner_id == user.get('id')).first()
    return recipes

@router.get("/views/")
async def get_views(db:db_dependency,user:user_dependency):
    recipes = db.query(Recipes).filter(Recipes.views == 'yes').all()
    return recipes


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_recipe(user:user_dependency,db:db_dependency,recipe_request:RecipeRequest):
   if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
   new_recipe = Recipes(
        name=recipe_request.name,
        description=recipe_request.description,
        ingredients=recipe_request.ingredients,
        make_time=recipe_request.make_time,
        difficulty=recipe_request.difficulty,
        is_public=recipe_request.is_public,
        views=0,
        owner_id=user.get("id")
    )
   db.add(new_recipe)
   db.commit()


@router.put("/{recipe_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_recipe(db:db_dependency,user:user_dependency,recipe_request:RecipeRequest,recipe_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')
    user_model=db.query(Recipes).filter(Recipes.id==recipe_id).filter(Recipes.owner_id==user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404,detail='recipe not found')
    
    user_model.name=recipe_request.name
    user_model.description=recipe_request.description
    user_model.ingredients=recipe_request.ingredients
    user_model.make_time=recipe_request.make_time
    user_model.difficulty=recipe_request.difficulty
    user_model.is_public=recipe_request.is_public
    user_model.views=recipe_request.views
    
    db.add(user_model)
    db.commit()

@router.delete("/{recipe_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(db:db_dependency,user:user_dependency,recipe_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')
    user_model=db.query(Recipes).filter(Recipes.id==recipe_id).filter(Recipes.owner_id==user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404,detail='recipe not found')
    
    db.query(Recipes).filter(Recipes.id==recipe_id).filter(Recipes.owner_id==user.get('id')).delete()
    db.commit()
    