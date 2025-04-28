"""
Message Send Schema Module

This module defines the schema for message sending operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class SendMessageRequest(BaseModel):
    """
    Schema for send message request.
    """
    content: str = Field(..., description="Content of the message")
    sender_id: str = Field(..., description="ID of the message sender")
    recipient_id: Optional[str] = Field(None, description="ID of the message recipient")
    message_type: Optional[str] = Field("text", description="Type of message (text, command, etc.)")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Context information for the message")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class SendMessageResponse(BaseModel):
    """
    Schema for send message response.
    """
    message_id: str = Field(..., description="Unique identifier for the sent message")
    status: str = Field(..., description="Status of the operation")
    timestamp: str = Field(..., description="Timestamp when the message was sent")
    sender_id: str = Field(..., description="ID of the message sender")
    recipient_id: Optional[str] = Field(None, description="ID of the message recipient")
    delivery_status: str = Field(..., description="Delivery status of the message")
