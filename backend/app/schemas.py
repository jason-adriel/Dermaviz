from typing import Optional, List, Union
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# ---------- Base Config ----------
class CamelModel(BaseModel):
    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        alias_generator = lambda s: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(s.split('_'))
        )
        populate_by_name = True


# ---------- User ----------
class UserBase(CamelModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str


# ---------- Result ----------
class ResultBase(CamelModel):
    raw_predictions: Optional[str] = Field(None, alias="rawPredictions")

class ResultCreate(ResultBase):
    prediction: Optional[bytes]
    report: Optional[bytes]

class ResultOut(ResultBase):
    id: str
    prediction: Optional[bytes]
    report: Optional[bytes]


# ---------- Submission Detail ----------
class SubmissionDetailBase(CamelModel):
    sex_at_birth: Optional[str] = Field(None, alias="sexAtBirth")
    age_group: Optional[str] = Field(None, alias="ageGroup")
    textures: Optional[Union[dict, list]]
    body_parts: Optional[Union[dict, list]] = Field(None, alias="bodyParts")
    condition_symptoms: Optional[Union[dict, list]] = Field(None, alias="conditionSymptoms")
    condition_duration: Optional[str] = Field(None, alias="conditionDuration")

class SubmissionDetailCreate(SubmissionDetailBase):
    image: Optional[bytes]

class SubmissionDetailOut(SubmissionDetailBase):
    id: str
    image: Optional[bytes]


# ---------- Submission Queue ----------
class SubmissionQueueBase(CamelModel):
    name: str
    status: Optional[str]
    processing_time: Optional[datetime] = Field(None, alias="processingTime")
    submission_time: Optional[datetime] = Field(None, alias="submissionTime")
    completion_time: Optional[datetime] = Field(None, alias="completionTime")

class SubmissionQueueCreate(SubmissionQueueBase):
    user_id: str = Field(..., alias="userId")
    result_id: Optional[str] = Field(None, alias="resultId")

class SubmissionQueueOut(SubmissionQueueBase):
    id: str
    user: Optional[UserOut]
    result: Optional[ResultOut]
    details: List[SubmissionDetailOut] = []
