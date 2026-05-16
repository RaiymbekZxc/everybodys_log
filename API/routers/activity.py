
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..timpestampupdater import get_current_period
from ..auth import get_current_user, database_save
from ..models import tblUser, CategoryType, tblCategory, ActivityInfo
from ..database import SessionDep

router = APIRouter(prefix="/activity", dependencies=[Depends(get_current_user)])

@router.get("/info")
def act_persentages(session: SessionDep) -> ActivityInfo:
    response = ActivityInfo()
    response.timestamp = get_current_period()
    overall = 0
    info = session.exec(select(tblCategory)).all()

    for cat in info:
        overall += cat.PeopleClicked

    for cat in info:
        if cat.Name == CategoryType.leisure.value:
            response.leisure.count = cat.PeopleClicked
            response.leisure.percentage = int(cat.PeopleClicked / overall * 100) if overall != 0 else 0

        if cat.Name == CategoryType.productivity.value:
            response.productivity.count = cat.PeopleClicked
            response.productivity.percentage = int(cat.PeopleClicked / overall * 100) if overall != 0 else 0

        if cat.Name == CategoryType.social_life.value:
            response.social_life.count = cat.PeopleClicked
            response.social_life.percentage = int(cat.PeopleClicked / overall * 100) if overall != 0 else 0

    
    return response

@router.post("/{category}")
def select_category(category: CategoryType, session: SessionDep, user: tblUser = Depends(get_current_user)):
    print(tblCategory, category.value)
    cat = session.exec(select(tblCategory).where(tblCategory.Name==category.value)).first()
    
    if not cat:
        raise HTTPException(404, detail="Invalid category")
    
    cat.PeopleClicked += 1

    database_save(session=session, dbinstance=cat)

    return {"detail": "click registered in the database."}
