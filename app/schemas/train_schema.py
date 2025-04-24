"""
Train Schema

This module defines the schemas for model training endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class TrainingModel(str, Enum):
    """Models available for training."""
    CLASSIFIER = "classifier"
    REGRESSION = "regression"
    EMBEDDING = "embedding"
    SUMMARIZATION = "summarization"
    GENERATION = "generation"
    CUSTOM = "custom"


class TrainingDataFormat(str, Enum):
    """Data formats for training."""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    JSONL = "jsonl"


class TrainRequest(BaseModel):
    """Request schema for model training."""
    model_type: TrainingModel = Field(
        ..., 
        description="Type of model to train"
    )
    training_data: Union[str, Dict[str, Any], List[Dict[str, Any]]] = Field(
        ..., 
        description="Training data (string, object, or array)"
    )
    data_format: TrainingDataFormat = Field(
        TrainingDataFormat.JSON, 
        description="Format of the training data"
    )
    model_name: str = Field(
        ..., 
        description="Name for the trained model"
    )
    hyperparameters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Hyperparameters for training"
    )
    validation_split: Optional[float] = Field(
        0.2, 
        description="Fraction of data to use for validation"
    )
    max_epochs: Optional[int] = Field(
        10, 
        description="Maximum number of training epochs"
    )
    agent_id: Optional[str] = Field(
        None, 
        description="Agent ID requesting the training"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop ID associated with the training"
    )
    
    @validator('model_name')
    def model_name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('model_name must not be empty')
        if len(v) > 64:
            raise ValueError('model_name must be at most 64 characters')
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError('model_name must contain only alphanumeric characters, hyphens, and underscores')
        return v
    
    @validator('validation_split')
    def validation_split_must_be_valid(cls, v):
        if v is not None and (v < 0.0 or v > 0.5):
            raise ValueError('validation_split must be between 0.0 and 0.5')
        return v
    
    @validator('max_epochs')
    def max_epochs_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('max_epochs must be positive')
        if v is not None and v > 100:
            return 100  # Cap at 100 for performance
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "model_type": "classifier",
                "training_data": [
                    {"text": "I love this product", "label": "positive"},
                    {"text": "This product is terrible", "label": "negative"},
                    {"text": "Average product, nothing special", "label": "neutral"}
                ],
                "data_format": "json",
                "model_name": "sentiment-classifier-v1",
                "hyperparameters": {
                    "learning_rate": 0.001,
                    "batch_size": 32
                },
                "validation_split": 0.2,
                "max_epochs": 10,
                "agent_id": "TRAINER",
                "loop_id": "loop_12345"
            }
        }


class TrainingMetrics(BaseModel):
    """Schema for training metrics."""
    accuracy: Optional[float] = Field(None, description="Accuracy metric (for classification)")
    precision: Optional[float] = Field(None, description="Precision metric (for classification)")
    recall: Optional[float] = Field(None, description="Recall metric (for classification)")
    f1_score: Optional[float] = Field(None, description="F1 score (for classification)")
    loss: float = Field(..., description="Training loss")
    val_loss: Optional[float] = Field(None, description="Validation loss")
    epochs_completed: int = Field(..., description="Number of epochs completed")
    training_time: float = Field(..., description="Training time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "accuracy": 0.92,
                "precision": 0.91,
                "recall": 0.93,
                "f1_score": 0.92,
                "loss": 0.15,
                "val_loss": 0.18,
                "epochs_completed": 10,
                "training_time": 120.5
            }
        }


class TrainResponse(BaseModel):
    """Response schema for model training."""
    model_id: str = Field(..., description="Unique identifier for the trained model")
    model_name: str = Field(..., description="Name of the trained model")
    model_type: TrainingModel = Field(..., description="Type of model trained")
    status: str = Field(..., description="Training status (e.g., 'completed', 'failed')")
    metrics: Optional[TrainingMetrics] = Field(None, description="Training metrics")
    examples_processed: int = Field(..., description="Number of examples processed during training")
    model_size: Optional[int] = Field(None, description="Size of the trained model in bytes")
    agent_id: Optional[str] = Field(None, description="Agent ID that requested the training")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the training")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the training completion"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "model_12345",
                "model_name": "sentiment-classifier-v1",
                "model_type": "classifier",
                "status": "completed",
                "metrics": {
                    "accuracy": 0.92,
                    "precision": 0.91,
                    "recall": 0.93,
                    "f1_score": 0.92,
                    "loss": 0.15,
                    "val_loss": 0.18,
                    "epochs_completed": 10,
                    "training_time": 120.5
                },
                "examples_processed": 1000,
                "model_size": 5242880,
                "agent_id": "TRAINER",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class TrainError(BaseModel):
    """Error response schema for model training."""
    message: str = Field(..., description="Error message")
    model_type: Optional[TrainingModel] = Field(None, description="Requested model type if available")
    model_name: Optional[str] = Field(None, description="Requested model name if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to train model: Insufficient training data",
                "model_type": "classifier",
                "model_name": "sentiment-classifier-v1",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class TrainStatusRequest(BaseModel):
    """Request schema for checking training status."""
    model_id: str = Field(..., description="Unique identifier for the model")
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "model_12345"
            }
        }


class TrainStatusResponse(BaseModel):
    """Response schema for training status."""
    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    status: str = Field(..., description="Training status (e.g., 'queued', 'in_progress', 'completed', 'failed')")
    progress: Optional[float] = Field(None, description="Training progress as a percentage")
    current_epoch: Optional[int] = Field(None, description="Current training epoch")
    total_epochs: Optional[int] = Field(None, description="Total number of epochs")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time (ISO timestamp)")
    error_message: Optional[str] = Field(None, description="Error message if training failed")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the status check"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "model_12345",
                "model_name": "sentiment-classifier-v1",
                "status": "in_progress",
                "progress": 45.0,
                "current_epoch": 5,
                "total_epochs": 10,
                "estimated_completion": "2025-04-24T21:15:00Z",
                "error_message": None,
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }
