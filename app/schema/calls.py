from pydantic import BaseModel, Field
from typing import Optional

class CallRequest(BaseModel):
    """Schema for call initiation request"""
    destination: str = Field(..., description="Destination phone number to call")
    caller_id: Optional[str] = Field(None, description="Caller ID to use for this call")
    gateway: Optional[str] = Field(None, description="Gateway to use for this call")
    timeout: Optional[int] = Field(60, description="Call timeout in seconds")
    variables: Optional[dict] = Field(None, description="Additional channel variables")

class CallResponse(BaseModel):
    """Schema for call initiation response"""
    success: bool
    message: str
    call_uuid: Optional[str] = None 