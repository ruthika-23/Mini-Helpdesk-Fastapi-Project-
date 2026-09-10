"""
FastAPI Backend Application for Mini Helpdesk.
Provides REST API endpoints for managing tickets and viewing dashboard metrics.
"""

from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

from database import tickets_collection, ticket_helper, check_connection
from models import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    DashboardMetrics,
    Status,
    Priority
)

app = FastAPI(
    title="Mini Helpdesk API",
    description="A clean, beginner-friendly REST API for managing support tickets with MongoDB Atlas.",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def read_root():
    """
    Root endpoint: Provides API status and verifies database connection.
    """
    is_connected, db_message = check_connection()
    return {
        "message": "Welcome to Mini Helpdesk API",
        "status": "Running",
        "database": db_message if not is_connected else "Connected",
        "docs_url": "/docs"
    }


@app.get("/tickets", response_model=List[TicketResponse], tags=["Tickets"])
def get_all_tickets(search: Optional[str] = Query(None, description="Search term for title or Ticket ID")):
    """
    Retrieve all support tickets, sorted by creation time (most recent first).
    Optional query parameter `search` filters by title or exact ticket ID.
    """
    try:
        query = {}
        if search:
            search = search.strip()
            # If search string is a valid ObjectId, search by ID or title
            if ObjectId.is_valid(search):
                query = {
                    "$or": [
                        {"_id": ObjectId(search)},
                        {"title": {"$regex": search, "$options": "i"}}
                    ]
                }
            else:
                # Search by title using case-insensitive regex
                query = {"title": {"$regex": search, "$options": "i"}}

        cursor = tickets_collection.find(query).sort("_id", -1)
        tickets = [ticket_helper(doc) for doc in cursor]
        return tickets
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching tickets: {str(e)}"
        )


@app.get("/tickets/{ticket_id}", response_model=TicketResponse, tags=["Tickets"])
def get_ticket_by_id(ticket_id: str):
    """
    Retrieve a single ticket by its unique Ticket ID (24-character hex string).
    """
    if not ObjectId.is_valid(ticket_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticket ID format: '{ticket_id}'. Must be a valid 24-character hexadecimal string."
        )

    try:
        ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with ID '{ticket_id}' not found."
            )
        return ticket_helper(ticket)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(ticket_data: TicketCreate):
    """
    Create a new support ticket.
    Default status is set to 'Open' and current UTC timestamp is saved as 'created_at'.
    """
    try:
        new_ticket = {
            "user_name": ticket_data.user_name.strip(),
            "email": ticket_data.email.strip(),
            "title": ticket_data.title.strip(),
            "description": ticket_data.description.strip(),
            "category": ticket_data.category.value,
            "priority": ticket_data.priority.value,
            "status": Status.OPEN.value,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        result = tickets_collection.insert_one(new_ticket)
        created_ticket = tickets_collection.find_one({"_id": result.inserted_id})
        return ticket_helper(created_ticket)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(e)}"
        )


@app.put("/tickets/{ticket_id}", response_model=TicketResponse, tags=["Tickets"])
def update_ticket_status(ticket_id: str, update_data: TicketUpdate):
    """
    Update the status of an existing ticket (Open, In Progress, or Resolved).
    """
    if not ObjectId.is_valid(ticket_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticket ID format: '{ticket_id}'."
        )

    try:
        result = tickets_collection.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$set": {"status": update_data.status.value}}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with ID '{ticket_id}' not found."
            )

        updated_ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
        return ticket_helper(updated_ticket)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update ticket: {str(e)}"
        )


@app.delete("/tickets/{ticket_id}", tags=["Tickets"])
def delete_ticket(ticket_id: str):
    """
    Delete a ticket using its unique ticket ID.
    """
    if not ObjectId.is_valid(ticket_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticket ID format: '{ticket_id}'."
        )

    try:
        result = tickets_collection.delete_one({"_id": ObjectId(ticket_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with ID '{ticket_id}' not found."
            )

        return {
            "message": f"Ticket with ID '{ticket_id}' was successfully deleted.",
            "ticket_id": ticket_id
        }
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete ticket: {str(e)}"
        )


@app.get("/dashboard", response_model=DashboardMetrics, tags=["Dashboard"])
def get_dashboard_metrics():
    """
    Retrieve aggregated statistics for tickets:
    - Total Tickets
    - Open Tickets
    - In Progress Tickets
    - Resolved Tickets
    - High Priority Tickets
    """
    try:
        total_tickets = tickets_collection.count_documents({})
        open_tickets = tickets_collection.count_documents({"status": Status.OPEN.value})
        in_progress_tickets = tickets_collection.count_documents({"status": Status.IN_PROGRESS.value})
        resolved_tickets = tickets_collection.count_documents({"status": Status.RESOLVED.value})
        high_priority_tickets = tickets_collection.count_documents({"priority": Priority.HIGH.value})

        return DashboardMetrics(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            in_progress_tickets=in_progress_tickets,
            resolved_tickets=resolved_tickets,
            high_priority_tickets=high_priority_tickets
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while calculating dashboard metrics: {str(e)}"
        )
