
from fastapi import APIRouter, Depends, Query
from ..models import CategoryType, tblUsersText, userOut, categories, UsersTextOut
from ..database import SessionDep
from ..auth import get_current_user, database_save
from sqlmodel import select

router = APIRouter(prefix="/posts", dependencies=[Depends(get_current_user)])

@router.post("/activity")
async def activity_post(text: str, category: CategoryType, session: SessionDep, current_user: userOut = Depends(get_current_user)):
    
    
    ut = tblUsersText(
        Activity=categories[category],
        Text=text,
        Author=current_user.UserId)
    

    database_save(session=session, dbinstance=ut)

    return {"details": "OK"}

@router.get("/{category}", response_model=list[UsersTextOut])
async def posts(session: SessionDep, category: CategoryType, page: int = Query(default=1, ge=1)):
    offset = (page - 1) * 5
    
    posts = session.exec(select(tblUsersText).where(tblUsersText.Activity == categories[category]).offset(offset).limit(5)).all()

    return posts

