from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from db.session import SessionLocal
from models.user import User
from models.role import Role
from schemas.auth_schema import RegisterSchema, LoginSchema
from core.hash import hash_password, verify_password
from core.jwt import create_access_token, create_refresh_token, decode_token,create_verification_token
from utils.email import send_verification_email
import os

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


from datetime import datetime, timedelta
from fastapi import HTTPException

EMAIL_VERIFY_EXPIRE_MIN = int(os.getenv("EMAIL_VERIFY_EXPIRE_MIN", 30))


@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if user:

  
        if user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

 
        if user.verification_sent_at:

            expire_time = user.verification_sent_at + timedelta(minutes=EMAIL_VERIFY_EXPIRE_MIN)

            if datetime.now(timezone.utc) < expire_time:
                raise HTTPException(
                    status_code=400,
                    detail="Verification link already sent"
                )

  
        token = create_verification_token(user.id)

        user.verification_token = token
        user.verification_sent_at = datetime.now(timezone.utc)

        db.commit()

        send_verification_email(user.email, token)

        return {"message": "Verification email resent"}

 
    new_user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_verification_token(new_user.id)

    new_user.verification_token = token
    new_user.verification_sent_at = datetime.now(timezone.utc)

    db.commit()

    send_verification_email(new_user.email, token)

    return {"message": "Verification email sent"}


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.password):

        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email"
        )

    access_token = create_access_token({"user_id": user.id})

    refresh_token = create_refresh_token({"user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
@router.post("/refresh")
def refresh(refresh_token: str):

    payload = decode_token(refresh_token)

    if not payload or payload["type"] != "refresh":

        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token({"user_id": payload["user_id"]})

    new_refresh = create_refresh_token({"user_id":payload["user_id"]})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }

    


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

    if payload.get("type") != "email_verify":
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )

    user_id = payload.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return {"message": "Email verified successfully"}