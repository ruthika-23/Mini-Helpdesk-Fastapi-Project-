"""
Database connection and helper utilities for MongoDB Atlas.
Uses PyMongo to interact with the database and safely format documents.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Look for .env in current directory and parent directory (project root)
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Read MongoDB configuration from environment variables
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017"
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "helpdesk_db")

# Initialize MongoClient with a 5-second server selection timeout
client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]
tickets_collection = db["tickets"]


def check_connection() -> tuple[bool, str]:
    """
    Checks if the connection to MongoDB Atlas is alive.
    Returns (True, "Connected") or (False, "Error message").
    """
    try:
        # Ping command tests connectivity and authentication
        client.admin.command("ping")
        return True, "Connected"
    except ConnectionFailure as e:
        return False, f"Connection Failure: {str(e)}"
    except Exception as e:
        return False, f"Database Error: {str(e)}"



def ticket_helper(ticket: dict) -> dict:
    """
    Helper function to convert a MongoDB document to a clean Python dictionary.
    Converts the internal MongoDB ObjectId '_id' into a JSON-serializable string 'id'.
    """
    if not ticket:
        return None
    return {
        "id": str(ticket["_id"]),
        "user_name": ticket.get("user_name", ""),
        "email": ticket.get("email", ""),
        "title": ticket.get("title", ""),
        "description": ticket.get("description", ""),
        "category": ticket.get("category", ""),
        "priority": ticket.get("priority", ""),
        "status": ticket.get("status", "Open"),
        "created_at": ticket.get("created_at", ""),
    }
