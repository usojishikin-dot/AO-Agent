# app/schemas/responses.py
from pydantic import BaseModel


class IngestionResponse(BaseModel):
    status: str
    external_id: str
    trace_id: str
    message: str