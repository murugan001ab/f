from fastapi import APIRouter, Depends,HTTPException

from sqlalchemy.orm import Session

from db.session import SessionLocal     
from models.user import User


service = APIRouter(prefix="/services", tags=["Services"])

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@service.get("/user/{user_id}")
async def get_user_services(user_id: int, db: Session = Depends(get_db)):

    user = await db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user_id": user.id, "name": user.name, "email": user.email}

