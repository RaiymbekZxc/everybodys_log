
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from ..auth import is_admin, get_user, save_user, delete_user, get_user_or_404, not_me_or_400, get_current_user
from ..database import SessionDep, SUPERKEY
from ..models import tblUser

router = APIRouter(prefix="/admin", dependencies=[Depends(is_admin)])

@router.put('/user/{username}/giveadmin')
async def user_give_admin(username: str, session: SessionDep):
    
    user = get_user_or_404(username=username, session=session)


@router.put('/user/{username}/deactivate')
async def user_deactivate(username: str, session: SessionDep, me: tblUser = Depends(get_current_user)):
    
    user = get_user_or_404(username=username, session=session)
    not_me_or_400(user, me)

    user.IsActive = False
    save_user(user=user, session=session)

    return {"detail": f"{user.Username} is deactivated."}

@router.delete('/user/{username}/delete')
async def user_delete(username: str, session: SessionDep, me: tblUser = Depends(get_current_user)):

    user = get_user_or_404(username=username, session=session)
    not_me_or_400(user, me)
    delete_user(user=user, session=session)

    return {"detail": f"{user.Username} account has been deleted."}