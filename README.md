# 🎫 Mini Helpdesk

A clean, beginner-friendly, and fully functional full-stack support ticket management system built with **FastAPI**, **Streamlit**, **MongoDB Atlas**, and **Docker**.

---

## 📑 Table of Contents

- [Architecture & Data Flow](#architecture--data-flow)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [MongoDB Atlas Setup Guide](#mongodb-atlas-setup-guide)
- [Local Development Setup (Without Docker)](#local-development-setup-without-docker)
- [Docker Setup (With Docker Compose)](#docker-setup-with-docker-compose)
- [API Documentation & Testing (Swagger)](#api-documentation--testing-swagger)
- [Error Handling](#error-handling)

---

## 🏗️ Architecture & Data Flow

```text
Streamlit (Port 8501)
       ↓ (HTTP REST Requests)
FastAPI Backend (Port 8000)
       ↓ (PyMongo Driver)
MongoDB Atlas (helpdesk_db.tickets)
       ↓ (BSON Documents)
FastAPI Backend (Converts ObjectId to string 'id')
       ↓ (JSON Responses)
Streamlit (Port 8501 - Renders UI)
```

1. **User Interaction**: Users interact with the clean Streamlit web application to view metrics, submit tickets, search, update status, or delete tickets.
2. **HTTP Requests**: Streamlit sends standard REST API requests (`GET`, `POST`, `PUT`, `DELETE`) via Python's `requests` library to the FastAPI backend. **Streamlit never connects directly to MongoDB.**
3. **Validation & Business Logic**: FastAPI validates incoming request payloads using Pydantic models and enforces valid categories, priorities, and statuses.
4. **Database Persistence**: PyMongo executes queries against MongoDB Atlas cloud database collection `tickets`.
5. **Serialization**: MongoDB's internal `_id` (`ObjectId`) is converted to a standard JSON string `id`, preventing serialization errors before returning the response.

---

## 🛠️ Technology Stack

### Backend
* **Python 3.11**
* **FastAPI**: Modern, high-performance web framework for building APIs.
* **Uvicorn**: Lightning-fast ASGI server.
* **PyMongo**: Official Python driver for MongoDB.
* **Pydantic**: Data validation and type safety.
* **python-dotenv**: Reads environment variables from `.env`.

### Frontend
* **Streamlit**: Python framework for building interactive web applications.
* **Requests**: Clean HTTP library for communicating with FastAPI.
* **Pandas**: Data formatting and table rendering.

### Database
* **MongoDB Atlas**: Fully managed cloud NoSQL database.

### Deployment
* **Docker & Docker Compose**: Containerized multi-service deployment.

---

## 📁 Project Structure

```text
mini-helpdesk/
│
├── backend/
│   ├── main.py              # FastAPI endpoints & business logic
│   ├── database.py          # MongoDB Atlas connection & ObjectId helper
│   ├── models.py            # Pydantic schemas and Enums
│   ├── requirements.txt     # Backend dependencies
│   └── Dockerfile           # Backend container definition
│
├── frontend/
│   ├── app.py               # Streamlit application UI & API client
│   ├── requirements.txt     # Frontend dependencies
│   └── Dockerfile           # Frontend container definition
│
├── .env                     # Private environment variables (ignored by git)
├── .env.example             # Template environment variables
├── .gitignore               # Git ignore file
├── docker-compose.yml       # Docker Compose multi-container setup
└── README.md                # Project documentation
```

---

## ✨ Features

1. **Dashboard**: Shows metrics for Total Tickets, Open Tickets, In Progress Tickets, Resolved Tickets, and High Priority Tickets.
2. **Create Ticket**: Form with User Name, Email, Ticket Title, Description, Category (*Technical, Billing, Account, General*), and Priority (*Low, Medium, High*). Defaults to status **Open**.
3. **View All Tickets**: Interactive table with Ticket ID, User Name, Title, Category, Priority, Status, and Created Date.
4. **Search Ticket**: Look up tickets by Ticket ID (24-character hex) or keyword in the Title.
5. **Update Ticket**: Modify ticket status (*Open*, *In Progress*, *Resolved*) using its Ticket ID.
6. **Delete Ticket**: Remove a ticket permanently by its ID with confirmation and feedback.

---

## 🌐 MongoDB Atlas Setup Guide

Follow these beginner-friendly steps to configure your free MongoDB Atlas database:

1. **Create an Account**: Go to [mongodb.com/atlas](https://www.mongodb.com/atlas) and sign up for a free account.
2. **Create a Free Cluster**:
   - Choose the **M0 Free** shared cluster.
   - Select your preferred cloud provider (e.g. AWS) and the nearest region.
   - Click **Create Cluster**.
3. **Create Database User**:
   - In the left sidebar, navigate to **Security** → **Database Access**.
   - Click **Add New Database User**.
   - Select **Password Authentication**.
   - Enter a username and a strong password (remember these).
   - Set Built-in Role to **Read and write to any database**.
   - Click **Add User**.
4. **Configure Network Access**:
   - In the left sidebar, navigate to **Security** → **Network Access**.
   - Click **Add IP Address**.
   - For development, choose **Allow Access From Anywhere** (`0.0.0.0/0`) or add your current IP address.
   - Click **Confirm**.
5. **Retrieve Connection String**:
   - Navigate to **Deployments** → **Database**.
   - Click **Connect** next to your cluster.
   - Choose **Drivers** (Python / version 3.11 or later).
   - Copy the connection URI:
     ```text
     mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0
     ```
   - Replace `<username>` and `<password>` with the credentials created in Step 3.
6. **Configure `.env` File**:
   - Create a file named `.env` in the `mini-helpdesk` folder:
     ```env
     MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0
     DATABASE_NAME=helpdesk_db
     ```

---

## 💻 Local Development Setup (Without Docker)

You can run both FastAPI and Streamlit locally using **Windows PowerShell**:

### 1. Open Windows PowerShell & Navigate to Project

```powershell
cd mini-helpdesk
```

### 2. Create and Activate a Python Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

*(If PowerShell displays a script execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and reactivate).*

### 3. Install Dependencies

```powershell
# Install backend packages
pip install -r backend/requirements.txt

# Install frontend packages
pip install -r frontend/requirements.txt
```

### 4. Create the `.env` File

Ensure the `.env` file exists in `mini-helpdesk/.env` with your MongoDB credentials:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
DATABASE_NAME=helpdesk_db
```

### 5. Start the FastAPI Backend

Open a terminal window and run:

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

The backend will be available at:
* API Root: `http://localhost:8000`
* Interactive Swagger Docs: `http://localhost:8000/docs`

### 6. Start the Streamlit Frontend

Open a **second** terminal window, activate the virtual environment, and run:

```powershell
cd frontend
streamlit run app.py --server.port 8501
```

The frontend will automatically open in your default browser at:
* Streamlit UI: `http://localhost:8501`

---

## 🐳 Docker Setup (With Docker Compose)

To run the entire stack with Docker:

### 1. Build the Images

```powershell
docker compose build
```

### 2. Start the Containers

```powershell
docker compose up
```

*(Add `-d` to run in detached background mode: `docker compose up -d`)*

### 3. Access the Services

* **Streamlit Web UI**: [http://localhost:8501](http://localhost:8501)
* **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
* **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop the Containers

```powershell
docker compose down
```

---

## 🧪 API Documentation & Testing (Swagger)

FastAPI automatically serves interactive Swagger UI at **`http://localhost:8000/docs`**.

### 1. Create a Ticket
* **Method**: `POST`
* **URL**: `/tickets`
* **Request Body**:
```json
{
  "user_name": "Ruthika",
  "email": "ruthika@example.com",
  "title": "Unable to login",
  "description": "I cannot login to my account.",
  "category": "Account",
  "priority": "High"
}
```
* **Response Status**: `201 Created`

### 2. View All Tickets
* **Method**: `GET`
* **URL**: `/tickets`
* **Response Status**: `200 OK`

### 3. Search / Get Single Ticket by ID
* **Method**: `GET`
* **URL**: `/tickets/{ticket_id}` (e.g. `/tickets/65e90f23a1b2c3d4e5f67890`)
* **Response Status**: `200 OK`

### 4. Update Ticket Status
* **Method**: `PUT`
* **URL**: `/tickets/{ticket_id}`
* **Request Body**:
```json
{
  "status": "In Progress"
}
```
* **Response Status**: `200 OK`

### 5. Delete Ticket
* **Method**: `DELETE`
* **URL**: `/tickets/{ticket_id}`
* **Response Status**: `200 OK`
* **Response Body**:
```json
{
  "message": "Ticket with ID '65e90f23a1b2c3d4e5f67890' was successfully deleted.",
  "ticket_id": "65e90f23a1b2c3d4e5f67890"
}
```

### 6. View Dashboard Metrics
* **Method**: `GET`
* **URL**: `/dashboard`
* **Response Status**: `200 OK`
* **Response Body**:
```json
{
  "total_tickets": 1,
  "open_tickets": 0,
  "in_progress_tickets": 1,
  "resolved_tickets": 0,
  "high_priority_tickets": 1
}
```

---

## 🛡️ Error Handling

The application handles common edge cases with clear messages:
* **Invalid Ticket ID**: Returns `400 Bad Request` if the ticket ID is not a valid 24-character hexadecimal ObjectId.
* **Ticket Not Found**: Returns `404 Not Found` when attempting to fetch, update, or delete a non-existent ticket.
* **Validation Errors**: Returns `422 Unprocessable Entity` if required fields are missing or if invalid enum values are supplied.
* **Database / Network Failure**: Returns a clean `500 Internal Server Error` instead of crashing the server.
* **Frontend Resilience**: If the backend is stopped or unreachable, Streamlit displays an informative error card rather than an unhandled traceback.
