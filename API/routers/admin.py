
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from ..auth import is_admin, database_save, database_delete, get_user_or_404, not_me_or_400, get_current_user
from ..database import SessionDep, SUPERKEY
from ..models import tblUser, Super

router = APIRouter(prefix="/admin", dependencies=[Depends(is_admin)])
router_secret = APIRouter(prefix="/admin")

@router_secret.put('/user/{username}/makeadmin-through-superkey/', include_in_schema=False)
async def make_admin(superkey: Super, username:str, session: SessionDep):
    if superkey != SUPERKEY:
        raise HTTPException(403, "Wrong superkey.")
    
    user = get_user_or_404(username=username, session=session)

    if user.IsAdmin:
        raise HTTPException(400, "User is already admin.")
    
    user.IsAdmin = True
    
    database_save(dbinstance=user, session=session)
    
    return {"detail":f"Admin with username: {user.Username} is created."}

@router.put('/user/{username}/giveadmin')
async def user_give_admin(username: str, session: SessionDep, me: tblUser = Depends(get_current_user)):
    
    user = get_user_or_404(username=username, session=session)
    not_me_or_400(user, me)

    user.IsAdmin = True

    database_save(dbinstance=user, session=session)

    return {"detail": f"user {user.Username} is now admin"}

@router.put('/user/{username}/deactivate')
async def user_deactivate(username: str, session: SessionDep, me: tblUser = Depends(get_current_user)):
    
    user = get_user_or_404(username=username, session=session)
    not_me_or_400(user, me)

    user.IsActive = False
    database_save(dbinstance=user, session=session)

    return {"detail": f"{user.Username} is deactivated."}

@router.delete('/user/{username}/delete')
async def user_delete(username: str, session: SessionDep, me: tblUser = Depends(get_current_user)):

    user = get_user_or_404(username=username, session=session)
    
    not_me_or_400(user, me)
    database_delete(user=user, session=session)

    return {"detail": f"{user.Username} account has been deleted."}