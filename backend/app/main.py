from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from dotenv import load_dotenv
import models, schemas, crud
import os
from worker import start_worker, submission_queue
from database import engine, SessionLocal
from schemas import UserCreate, UserOut
from models import LoginRequest
import base64

models.Base.metadata.create_all(bind=engine)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()

origins = ["http://localhost:4200", "https://ringtail-regular-arguably.ngrok-free.app"]  # Modify for production
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class DeleteRequest(BaseModel):
    ids: List[str]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user

@app.on_event("startup")
def startup_event():
    print("Worker started!")
    start_worker()

@app.delete("/api/submissions")
def delete_submissions(request: DeleteRequest, db: Session = Depends(get_db)):
    submissions = db.query(models.SubmissionQueue).filter(models.SubmissionQueue.id.in_(request.ids)).all()

    if not submissions:
        raise HTTPException(status_code=404, detail="No matching submissions found")

    for submission in submissions:
        db.delete(submission)

    db.commit()


@app.post("/api/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/api/login")
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.email)
    if not user or not crud.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/logout")
def logout():
    return {"message": "Logged out successfully"}


@app.put("/api/user/update-name", response_model=UserOut)
def update_user_name(
    first_name: str,
    last_name: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.update_user_profile(db, user, first_name, last_name)


@app.put("/api/user/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    updated_user = crud.change_user_password(db, user, old_password, new_password)
    if not updated_user:
        raise HTTPException(status_code=403, detail="Old password incorrect.")
    return {"message": "Password updated successfully."}


@app.post("/api/submit-diagnosis")
async def submit_case(
    submissionName: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    texture: List[str] = Form(...),
    bodyParts: List[str] = Form(...),
    conditionSymptoms: List[str] = Form(...),
    conditionDuration: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user), 
):
    submission_id = str(uuid4())
    detail_id = str(uuid4())

    age_group = "AGE_18_TO_29"
    if (age > 29 and age < 40):
        age_group = "AGE_30_TO_39"
    elif (age > 39 and age < 50):
        age_group = "AGE_40_TO_49"
    elif (age > 49 and age < 60):
        age_group = "AGE_50_TO_59"
    elif (age > 59 and age < 70):
        age_group = "AGE_60_TO_69"
    elif (age > 69 and age < 80):
        age_group = "AGE_70_TO_79"
    elif (age > 79):
        age_group = "AGE_80_OR_ABOVE"

    # 0. Do validation checking, is current user already submitted more than 5 times?
    in_queue_count = db.query(models.SubmissionQueue).filter_by(
        user_id=current_user.id,
        status="IN QUEUE"
    ).count()

    if in_queue_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many submissions in queue. Please wait for them to be processed."
        )

    # 1. Store submission queue entry
    queue_entry = models.SubmissionQueue(
        id=submission_id,
        user_id=current_user.id,
        name=submissionName,
        status="IN QUEUE",
        submission_time=datetime.now(timezone.utc),
    )
    db.add(queue_entry)

    # 2. Store details
    detail_entry = models.SubmissionDetail(
        id=detail_id,
        submission_id=submission_id,
        image=await file.read(),
        sex_at_birth=gender,
        age_group=age_group,
        textures=texture,
        body_parts=bodyParts,
        condition_symptoms=conditionSymptoms,
        condition_duration=conditionDuration
    )
    db.add(detail_entry)
    db.commit()
    submission_queue.put(submission_id)
    return {"message": "Submission queued successfully", "id": submission_id}

@app.get("/api/submissions")
def get_my_submissions(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    submissions = db.query(models.SubmissionQueue).filter_by(user_id=user.id).order_by(models.SubmissionQueue.submission_time.desc()).all()

    return [
        {
            "id": sub.id,
            "name": sub.name,
            "status": sub.status,
            "resultId": sub.result_id,
            "submissionTime": sub.submission_time,
            "completionTime": sub.completion_time
        }
        for sub in submissions
    ]

@app.get("/api/results/{result_id}")
def get_result(result_id: str, db: Session = Depends(get_db)):
    result = db.query(models.Result).filter(models.Result.id == result_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    return {
        "id": str(result.id),
        "prediction": result.prediction,
        "image": base64.b64encode(result.report).decode("utf-8")  # convert bytes to base64
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )
