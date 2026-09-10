# 🎫 Mini Helpdesk

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge\&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge\&logo=streamlit)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge\&logo=mongodb)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge\&logo=docker)

### A clean and beginner-friendly Full-Stack Helpdesk Ticket Management System

**FastAPI ⚡ | Streamlit 🎨 | MongoDB Atlas ☁️ | Docker 🐳**

</div>

---

## 📌 Overview

**Mini Helpdesk** is a full-stack support ticket management system designed to simplify the process of creating, tracking, updating, and resolving customer support tickets.

The application uses **Streamlit** for the frontend, **FastAPI** for the REST API backend, and **MongoDB Atlas** for cloud-based data storage.

The complete application is containerized using **Docker and Docker Compose** for easy local development and deployment.

---

## 🏗️ Architecture & Data Flow

```text
┌──────────────────────┐
│      Streamlit       │
│      Frontend        │
└──────────┬───────────┘
           │
           │ HTTP REST API
           ▼
┌──────────────────────┐
│       FastAPI        │
│       Backend        │
└──────────┬───────────┘
           │
           │ PyMongo
           ▼
┌──────────────────────┐
│    MongoDB Atlas     │
│       Database       │
└──────────────────────┘
```

### Request Flow

```text
User
 ↓
Streamlit UI
 ↓
FastAPI REST API
 ↓
MongoDB Atlas
 ↓
FastAPI Response
 ↓
Streamlit UI
```

---

## 🛠️ Technology Stack

| Layer                | Technology            |
| -------------------- | --------------------- |
| Frontend             | Streamlit             |
| Backend              | FastAPI               |
| Programming Language | Python                |
| Database             | MongoDB Atlas         |
| Database Driver      | PyMongo               |
| API Server           | Uvicorn               |
| API Testing          | Swagger UI            |
| Containerization     | Docker                |
| Orchestration        | Docker Compose        |
| Configuration        | Environment Variables |

---

## 📂 Project Structure

```text
mini-helpdesk/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## ✨ Features

### 🎫 Ticket Management

* Create new support tickets
* View all tickets
* Search tickets
* View individual ticket details
* Update ticket status
* Delete tickets

### 📊 Dashboard

The dashboard provides quick statistics such as:

* Total tickets
* Open tickets
* In Progress tickets
* Resolved tickets
* High-priority tickets

### 🏷️ Ticket Categories

Tickets can be categorized into:

* 💻 Technical
* 💳 Billing
* 👤 Account
* 📌 General

### 🚦 Priority Levels

Each ticket can have one of the following priority levels:

* 🟢 Low
* 🟡 Medium
* 🔴 High

### 🔄 Ticket Status

Tickets follow a simple lifecycle:

```text
🆕 Open
   ↓
🔧 In Progress
   ↓
✅ Resolved
```

---

## 🗄️ MongoDB Database

The application uses **MongoDB Atlas** as the cloud database.

### Database

```text
helpdesk_db
```

### Collection

```text
tickets
```

### Ticket Document

```json
{
  "_id": "ObjectId",
  "user_name": "John Doe",
  "email": "john@example.com",
  "title": "Unable to login",
  "description": "I cannot access my account.",
  "category": "Account",
  "priority": "High",
  "status": "Open",
  "created_at": "2026-09-10T10:30:00"
}
```

---

# 🚀 Getting Started

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/ruthika-23/Mini-Helpdesk-Fastapi-Project-.git
```

```bash
cd Mini-Helpdesk-Fastapi-Project-
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

# ☁️ MongoDB Atlas Setup

## 1. Create a MongoDB Atlas Cluster

Create a MongoDB Atlas cluster and obtain your connection string.

Your connection string will look similar to:

```text
mongodb+srv://<username>:<password>@cluster.mongodb.net/
```

## 2. Create Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=helpdesk_db
```

> ⚠️ Never commit `.env` to GitHub because it may contain database credentials.

---

# ⚙️ Backend Setup

Move into the backend directory:

```powershell
cd backend
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
uvicorn main:app --reload
```

The backend will run at:

```text
http://localhost:8000
```

---

# 📖 API Documentation

FastAPI automatically provides interactive API documentation through Swagger UI.

Open:

```text
http://localhost:8000/docs
```

You can use Swagger to:

* View available APIs
* Send GET requests
* Create tickets
* Update tickets
* Delete tickets
* Test API responses

---

# 🔌 API Endpoints

| Method   | Endpoint               | Description           |
| -------- | ---------------------- | --------------------- |
| `GET`    | `/`                    | Check API status      |
| `GET`    | `/tickets`             | Get all tickets       |
| `GET`    | `/tickets/{ticket_id}` | Get a specific ticket |
| `POST`   | `/tickets`             | Create a new ticket   |
| `PUT`    | `/tickets/{ticket_id}` | Update a ticket       |
| `DELETE` | `/tickets/{ticket_id}` | Delete a ticket       |
| `GET`    | `/dashboard`           | Get ticket statistics |

---

# 📝 Create Ticket

### Endpoint

```text
POST /tickets
```

### Example Request

```json
{
  "user_name": "Ruthika",
  "email": "ruthika@example.com",
  "title": "Login Issue",
  "description": "Unable to login to the application.",
  "category": "Account",
  "priority": "High"
}
```

### Default Status

New tickets are created with:

```text
Open
```

---

# 🔍 Get Tickets

### Get All Tickets

```text
GET /tickets
```

Returns all available support tickets.

### Get a Specific Ticket

```text
GET /tickets/{ticket_id}
```

Example:

```text
GET /tickets/64f123abc456...
```

---

# 🔄 Update Ticket

### Endpoint

```text
PUT /tickets/{ticket_id}
```

The ticket status can be updated to:

```text
Open
In Progress
Resolved
```

Example:

```json
{
  "status": "Resolved"
}
```

---

# 🗑️ Delete Ticket

### Endpoint

```text
DELETE /tickets/{ticket_id}
```

Deletes the selected ticket from the database.

---

# 📊 Dashboard API

### Endpoint

```text
GET /dashboard
```

The dashboard API provides ticket statistics including:

```text
Total Tickets
Open Tickets
In Progress Tickets
Resolved Tickets
High Priority Tickets
```

---

# 🎨 Frontend

The frontend is developed using **Streamlit**.

Start the frontend from the `frontend` directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run Streamlit:

```powershell
streamlit run app.py
```

The application will open in the browser.

---

# 🐳 Docker Setup

Docker is used to containerize both the frontend and backend services.

The project uses **Docker Compose** to run multiple services together.

### Services

```text
┌─────────────────────┐
│      Frontend       │
│     Streamlit       │
│      Port 8501      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       Backend       │
│       FastAPI       │
│      Port 8000      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    MongoDB Atlas     │
└─────────────────────┘
```

---

## ▶️ Run with Docker Compose

From the project root:

```powershell
docker compose up --build
```

After the containers start:

### Streamlit

```text
http://localhost:8501
```

### FastAPI

```text
http://localhost:8000
```

### Swagger

```text
http://localhost:8000/docs
```

---

## 🛑 Stop Docker Containers

```powershell
docker compose down
```

---

# 🔐 Environment Variables

The project uses environment variables to keep configuration separate from source code.

### `.env`

```env
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=helpdesk_db
```

### `.env.example`

```env
MONGODB_URL=
DATABASE_NAME=helpdesk_db
```

> The actual `.env` file should never be pushed to GitHub.

---

# ⚠️ Error Handling

The backend handles common API errors such as:

* Invalid ticket ID
* Ticket not found
* Invalid request data
* Database-related errors
* Invalid ticket status

FastAPI returns appropriate HTTP responses for these situations.

---

# 🧪 API Testing

The APIs can be tested using:

* Swagger UI
* Browser for GET endpoints
* Postman
* Streamlit frontend

Swagger UI is available at:

```text
http://localhost:8000/docs
```

---

# 🧠 Key Concepts Practiced

This project demonstrates practical understanding of:

```text
REST APIs
   ↓
FastAPI
   ↓
CRUD Operations
   ↓
MongoDB
   ↓
Streamlit
   ↓
Docker
   ↓
Docker Compose
```

---

# 🎯 Learning Outcomes

Through this project, I practiced:

* Building REST APIs using FastAPI
* Creating CRUD operations
* Connecting FastAPI with MongoDB Atlas
* Working with MongoDB collections and documents
* Handling MongoDB ObjectId serialization
* Building interactive interfaces using Streamlit
* Connecting frontend and backend services
* Testing APIs using Swagger UI
* Using environment variables securely
* Containerizing applications with Docker
* Running multiple services using Docker Compose
* Understanding Docker service-to-service communication

---

# 🔮 Future Enhancements

Possible future improvements include:

* 🔐 User authentication and role-based access
* 👥 Admin and support-agent roles
* 💬 Ticket comments and conversation history
* 📎 File attachments
* 📧 Email notifications
* 📈 Advanced analytics
* 🔎 Advanced ticket filtering
* 🤖 AI-powered ticket classification
* 📊 More detailed support reports

---

# 📌 Project Highlights

```text
✅ Full-Stack Application
✅ REST API Architecture
✅ Cloud Database Integration
✅ CRUD Operations
✅ Interactive Dashboard
✅ Dockerized Application
✅ Docker Compose
✅ Swagger API Documentation
✅ Environment-Based Configuration
```

---

# 💡 Why This Project?

Mini Helpdesk was built to understand how a real-world application can be divided into independent layers:

```text
Frontend
   ↓
Backend API
   ↓
Database
```

It provides hands-on experience with **API development, database integration, frontend-backend communication, and containerization** using a simple and practical use case.

---

# 👩‍💻 Author

<div align="center">

### Ruthika B

**B.Tech Artificial Intelligence & Data Science**

Interested in **Web Development, Backend Development, AI & Data Technologies**

</div>

---

## ⭐ Support

If you found this project useful, consider giving the repository a ⭐.

<div align="center">

### 🎫 Mini Helpdesk

**Built with ❤️ using FastAPI • Streamlit • MongoDB Atlas • Docker**

</div>
