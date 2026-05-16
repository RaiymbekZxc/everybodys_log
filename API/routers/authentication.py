

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select
from datetime import timedelta
from typing import Annotated

from ..auth import (tblUser, authenticate_user, verify_password, create_access_token, get_user, 
                    get_current_user, get_password_hash,database_save, oauth2_scheme ,blacklisted_tokens)
from ..models import Token, UserCreate, UserUpdate, UpdateType, userOut
from ..database import SessionDep

router = APIRouter(prefix="/auth")

@router.get('/users/me', response_model=userOut)
async def read_users_me(current_user: Annotated[str, Depends(get_current_user)]):
    return current_user

@router.post('/token')
async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = await authenticate_user(session=session, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password.")

    access_token = create_access_token(data={"sub": str(user.UserId)}, expires_delta=timedelta(days=30))
    return Token(access_token=access_token, token_type="bearer")

@router.post('/register', status_code=201)
async def register_user(user_data: UserCreate, session: SessionDep):
    if get_user(session=session, username=user_data.Username):
        raise HTTPException(status_code=409, detail="Given username is already taken.")
    
    if get_user(session=session, email=user_data.Email):
        raise HTTPException(status_code=409, detail="Given email is already in use.")
    
    user = tblUser(**user_data.model_dump(exclude={"password"}), hashed_password=get_password_hash(user_data.Password))
    database_save(session=session, dbinstance=user)

    return {"detail": "user created."}

@router.post('/logout')
async def logout_user(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return {"detail": "logged out."}

@router.put('/users/me')
async def update_user(session: SessionDep, user_info: UserUpdate, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token=token, session=session)
    match user_info.TypeOfInteraction:
        case UpdateType.password:
            if not verify_password(user_info.Password, current_user.hashed_password): 
                raise HTTPException(status_code=401, detail="Incorrect password.")
            
            current_user.hashed_password = get_password_hash(user_info.NewPassword)
            
            database_save(dbinstance=current_user, session=session)
            
            return {"detail": "Password has been successfuly updated."}
        case UpdateType.username:

            if not user_info.Username:
                raise HTTPException(status_code=422, detail="No username provided.")
            statement = select(tblUser).where(user_info.Username==tblUser.Username)

            if session.exec(statement=statement).first():
                raise HTTPException(status_code=409, detail="Username already taken.")
            
            current_user.Username = user_info.Username
            
            database_save(dbinstance=current_user, session=session)
            
            return {"detail": "Username has been successfuly updated."}
