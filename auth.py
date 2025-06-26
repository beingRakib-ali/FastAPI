from fastapi import APIRouter, Depends,HTTPException
from datetime import timedelta, datetime
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import sessionlocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt,JWTError




router = APIRouter(prefix='/auth',tags=['auth'])

SECRET_KEY = 'ewdnowqiej£ª2º£h4rsjdo03289r43hb4343xx923232xhbfbhvsdncnowewe034'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type : str


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

@router.post('/create_user')
async def create_users(db:db_dependency,create_user_request:CreateUserRequest):
    create_user_model = Users(username = create_user_request.username,hashed_password = bcrypt_context.hash(create_user_request.password))

    db.add(create_user_model)
    db.commit()


@router.post('/token', response_model=Token)
async def loging_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = authentication_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not authenticated"
        )

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


def authentication_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


# ✅ JWT Token Generator
def create_access_token(username: str, id: int, expire_delta: timedelta):
    encode = {'sub': username, 'id': id}
    expires = datetime.utcnow() + expire_delta
    encode.update({'exp': expires})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt