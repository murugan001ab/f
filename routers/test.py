from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.user import User
from schemas.auth_schema import RegisterSchema
router = APIRouter(prefix="/auth", tags=["Auth"])
def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/login")
async def login(data: RegisterSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    return {"message": user.name}