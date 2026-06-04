
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from ..models import CategoryType, tblUsersText, userOut, categories, UsersTextOut, UserGet
from ..database import SessionDep
from ..auth import get_current_user, database_save, get_user
from sqlmodel import select, delete


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

@router.delete("/")
async def deletion(session: SessionDep, user: userOut = Depends(get_current_user)):
    statement = delete(tblUsersText).where(tblUsersText.Author == user.UserId)  # type: ignore
    session.exec(statement)
    return {"details": "Deleted."}

@router.get("/user/{type}/{info}")
async def getuser(session: SessionDep, type: UserGet, info: str):
    match type.value:
        case "id":
            user = get_user(session=session, id=int(info))
        case "email":
            user = get_user(session=session, email=info)
        case "username":
            user = get_user(session=session, username=info)
    if not user:
        raise HTTPException(404, detail="User not found")
    return user