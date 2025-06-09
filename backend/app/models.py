from sqlalchemy import Column, String, ForeignKey, DateTime, LargeBinary, JSON, CHAR, VARCHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class User(Base):
    __tablename__ = "user"

    id = Column(String(100), primary_key=True)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    submissions = relationship("SubmissionQueue", back_populates="user")


class SubmissionQueue(Base):
    __tablename__ = "submissionqueue"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("user.id"), nullable=False)
    result_id = Column(String(100), ForeignKey("result.id"), nullable=True)

    name = Column(String(20), nullable=False)
    status = Column(String(20), nullable=True)
    processing_time = Column(DateTime, nullable=True)
    submission_time = Column(DateTime, nullable=True)
    completion_time = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="submissions")
    result = relationship("Result", back_populates="submission", uselist=False)
    details = relationship("SubmissionDetail", back_populates="submission")


class SubmissionDetail(Base):
    __tablename__ = "submissiondetail"

    id = Column(String(100), primary_key=True)
    submission_id = Column(String(100), ForeignKey("submissionqueue.id"), nullable=False)

    image = Column(LargeBinary, nullable=True)
    sex_at_birth = Column(CHAR(1), nullable=True)
    age_group = Column(String(30), nullable=True)
    textures = Column(JSONB, nullable=True)
    body_parts = Column(JSONB, nullable=True)
    condition_symptoms = Column(JSONB, nullable=True)
    condition_duration = Column(String(30), nullable=True)

    submission = relationship("SubmissionQueue", back_populates="details")


class Result(Base):
    __tablename__ = "result"

    id = Column(String(100), primary_key=True)

    prediction = Column(LargeBinary, nullable=True)
    report = Column(LargeBinary, nullable=True)
    raw_predictions = Column(String(1024), nullable=True)

    submission = relationship("SubmissionQueue", back_populates="result")
