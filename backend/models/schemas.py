"""
models/schemas.py
Pydantic models for all request/response payloads and DB records.
Used for validation when deserialising upstream API responses and
for serialising data returned to the frontend.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

#* Auth *#

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class RefreshRequest(BaseModel):
    refresh_token: str

class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    role: Optional[str] = None

#* Image *#

class ImageResponse(BaseModel):
    image_id: str
    timestamp: str
    image_data_base64: str

#* Results *#

class ResultsResponse(BaseModel):
    image_id: str
    intensity_average: Optional[float] = None
    focus_score: Optional[float] = None
    classification_label: Optional[str] = None
    histogram: List[int] = Field(default_factory=list)

    def is_complete(self) -> bool:
        return (
            self.intensity_average is not None
            and self.focus_score is not None
            and self.classification_label is not None
        )

#* DB record *#

class SnapshotRecord(BaseModel):
    image_id: str
    timestamp: str
    intensity_average: float
    focus_score: float
    classification_label: str
    histogram_json: str          # JSON-encoded list[int]
    image_data_base64: str
    processed_data_base64: Optional[str] = None

#* API responses to frontend *#

class ImagePayload(BaseModel):
    """ /api/image response """
    image_id: str
    timestamp: str
    image_data_base64: str
    processed_data_base64: Optional[str] = None

class ResultsPayload(BaseModel):
    """ /api/results response """
    image_id: str
    intensity_average: Optional[float] = None
    focus_score: Optional[float] = None
    classification_label: Optional[str] = None
    histogram: List[int] = Field(default_factory=list)

class HistoryItem(BaseModel):
    image_id: str
    timestamp: str
    intensity_average: float
    focus_score: float
    classification_label: str
    histogram: List[int]
    image_data_base64: str
    processed_data_base64: Optional[str] = None

class StatsPayload(BaseModel):
    total_snapshots: int
    avg_intensity: float
    avg_focus: float
    label_counts: dict
