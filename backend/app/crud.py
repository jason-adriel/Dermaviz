from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User
from schemas import UserCreate
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: UserCreate):
    hashed = hash_password(user.password)
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        password=hashed,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user_profile(db: Session, user: User, first_name: str, last_name: str):
    user.first_name = first_name # type: ignore
    user.last_name = last_name # type: ignore
    db.commit()
    db.refresh(user)
    return user


def change_user_password(db: Session, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password):
        return None
    user.password = hash_password(new_password) # type: ignore
    db.commit()
    db.refresh(user)
    return user
