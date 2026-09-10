"""
Data models and schemas for the Mini Helpdesk application.
Defines Pydantic models and Enums for request validation and response formatting.
"""

from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class Category(str, Enum):
    """Allowed categories for a ticket."""
    TECHNICAL = "Technical"
    BILLING = "Billing"
    ACCOUNT = "Account"
    GENERAL = "General"


class Priority(str, Enum):
    """Allowed priorities for a ticket."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(str, Enum):
    """Allowed statuses for a ticket."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class TicketCreate(BaseModel):
    """Schema for creating a new support ticket."""
    user_name: str = Field(..., min_length=1, description="Name of the user submitting the ticket", example="Ruthika")
    email: str = Field(..., min_length=3, description="User contact email address", example="user@example.com")
    title: str = Field(..., min_length=1, description="Brief summary of the issue", example="Login problem")
    description: str = Field(..., min_length=1, description="Detailed description of the issue", example="Unable to login")
    category: Category = Field(..., description="Category of the ticket", example=Category.ACCOUNT)
    priority: Priority = Field(..., description="Priority level", example=Priority.HIGH)


class TicketUpdate(BaseModel):
    """Schema for updating an existing ticket's status."""
    status: Status = Field(..., description="New status for the ticket", example=Status.IN_PROGRESS)


class TicketResponse(BaseModel):
    """Schema for returning ticket details to the client (with string id)."""
    id: str = Field(..., description="Unique ticket identifier (converted from MongoDB ObjectId)")
    user_name: str
    email: str
    title: str
    description: str
    category: Category
    priority: Priority
    status: Status
    created_at: str


class DashboardMetrics(BaseModel):
    """Schema for aggregated dashboard metrics."""
    total_tickets: int = 0
    open_tickets: int = 0
    in_progress_tickets: int = 0
    resolved_tickets: int = 0
    high_priority_tickets: int = 0
