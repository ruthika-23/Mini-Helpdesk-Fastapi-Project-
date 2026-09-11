"""
Streamlit Frontend Application for Mini Helpdesk.
Communicates strictly with the FastAPI backend REST API.
"""

import os
import requests
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Read backend URL from environment variable or Streamlit secrets with localhost fallback
BACKEND_URL = os.getenv("BACKEND_URL")
if not BACKEND_URL:
    try:
        BACKEND_URL = st.secrets.get("BACKEND_URL")
    except Exception:
        pass
if not BACKEND_URL:
    BACKEND_URL = "http://localhost:8000"
BACKEND_URL = BACKEND_URL.rstrip("/")


st.set_page_config(
    page_title="Mini Helpdesk",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for clean aesthetics
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }
    .ticket-card {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helper Functions for API Calls
# -----------------------------------------------------------------------------
def fetch_api(endpoint: str, method: str = "GET", data: dict = None, params: dict = None):
    """
    Generic HTTP client helper to call the FastAPI backend.
    Catches connection errors and formats user-friendly error messages.
    """
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return False, {"detail": f"Unsupported HTTP method: {method}"}

        # Parse response JSON if possible
        try:
            res_json = response.json()
        except Exception:
            res_json = {"detail": response.text}

        if response.status_code in (200, 201):
            return True, res_json
        else:
            error_message = res_json.get("detail", "An unexpected error occurred.")
            return False, {"detail": error_message}

    except requests.exceptions.ConnectionError:
        return False, {
            "detail": f"Could not connect to FastAPI backend at {BACKEND_URL}. Please ensure the backend server is running."
        }
    except requests.exceptions.Timeout:
        return False, {"detail": "Request timed out while contacting the backend server."}
    except Exception as e:
        return False, {"detail": str(e)}


# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/customer-support.png", width=70)
st.sidebar.title("Mini Helpdesk")
st.sidebar.caption("Ticket Management System")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "Dashboard",
        "Create Ticket",
        "View Tickets",
        "Search Ticket",
        "Update Ticket",
        "Delete Ticket"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption(f"**Backend:** `{BACKEND_URL}`")


# -----------------------------------------------------------------------------
# 1. Dashboard Page
# -----------------------------------------------------------------------------
if menu == "Dashboard":
    st.markdown('<div class="main-title">📊 Helpdesk Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-time overview of support ticket workload</div>', unsafe_allow_html=True)

    success, data = fetch_api("/dashboard")

    if not success:
        st.error(f"❌ {data['detail']}")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📋 Total Tickets", data.get("total_tickets", 0))
        col2.metric("🔵 Open", data.get("open_tickets", 0))
        col3.metric("🟡 In Progress", data.get("in_progress_tickets", 0))
        col4.metric("🟢 Resolved", data.get("resolved_tickets", 0))
        col5.metric("🚨 High Priority", data.get("high_priority_tickets", 0))

        st.markdown("---")

        # Quick breakdown section
        st.subheader("System Status")
        status_success, status_data = fetch_api("/")
        if status_success:
            st.success(f"**FastAPI Backend:** {status_data.get('status')} | **Database:** {status_data.get('database')}")
        else:
            st.warning("Backend connectivity check failed.")


# -----------------------------------------------------------------------------
# 2. Create Ticket Page
# -----------------------------------------------------------------------------
elif menu == "Create Ticket":
    st.markdown('<div class="main-title">➕ Create Support Ticket</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Submit a new inquiry or issue for resolution</div>', unsafe_allow_html=True)

    with st.form("create_ticket_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("User Name *", placeholder="e.g. Ruthika")
            category = st.selectbox("Category *", ["Technical", "Billing", "Account", "General"])
        with col2:
            email = st.text_input("Email Address *", placeholder="e.g. user@example.com")
            priority = st.selectbox("Priority *", ["Low", "Medium", "High"], index=1)

        title = st.text_input("Ticket Title *", placeholder="e.g. Unable to access billing dashboard")
        description = st.text_area("Description *", placeholder="Provide detailed information regarding the problem...")

        submitted = st.form_submit_button("Submit Ticket", use_container_width=True)

        if submitted:
            if not user_name or not email or not title or not description:
                st.error("⚠️ Please fill in all required fields marked with *.")
            else:
                payload = {
                    "user_name": user_name,
                    "email": email,
                    "title": title,
                    "description": description,
                    "category": category,
                    "priority": priority
                }
                success, response_data = fetch_api("/tickets", method="POST", data=payload)
                if success:
                    st.success(f"✅ Ticket created successfully! Assigned ID: `{response_data.get('id')}`")
                    st.json(response_data)
                else:
                    st.error(f"❌ Failed to create ticket: {response_data['detail']}")


# -----------------------------------------------------------------------------
# 3. View Tickets Page
# -----------------------------------------------------------------------------
elif menu == "View Tickets":
    st.markdown('<div class="main-title">📋 View All Tickets</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">List of all active and past support tickets</div>', unsafe_allow_html=True)

    if st.button("🔄 Refresh Tickets"):
        st.rerun()

    success, tickets = fetch_api("/tickets")

    if not success:
        st.error(f"❌ {tickets['detail']}")
    elif not tickets:
        st.info("ℹ️ No tickets found in the database. Use 'Create Ticket' to add one.")
    else:
        # Prepare DataFrame with required fields
        display_data = []
        for t in tickets:
            display_data.append({
                "Ticket ID": t.get("id"),
                "User Name": t.get("user_name"),
                "Title": t.get("title"),
                "Category": t.get("category"),
                "Priority": t.get("priority"),
                "Status": t.get("status"),
                "Created Date": t.get("created_at")
            })

        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Showing **{len(tickets)}** ticket(s).")


# -----------------------------------------------------------------------------
# 4. Search Ticket Page
# -----------------------------------------------------------------------------
elif menu == "Search Ticket":
    st.markdown('<div class="main-title">🔍 Search Tickets</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Search tickets by unique Ticket ID or Title keyword</div>', unsafe_allow_html=True)

    search_query = st.text_input("Enter Ticket ID or Title keyword", placeholder="e.g. 68c123... or Login")

    if st.button("Search", use_container_width=True) or search_query:
        if not search_query.strip():
            st.warning("Please enter a search term.")
        else:
            success, results = fetch_api("/tickets", params={"search": search_query.strip()})
            if not success:
                st.error(f"❌ {results['detail']}")
            elif not results:
                st.info(f"No tickets matching '{search_query}' were found.")
            else:
                st.success(f"Found {len(results)} matching ticket(s):")
                for t in results:
                    with st.expander(f"🎫 {t.get('title')} (Status: {t.get('status')})", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Ticket ID:** `{t.get('id')}`")
                            st.write(f"**User Name:** {t.get('user_name')}")
                            st.write(f"**Email:** {t.get('email')}")
                        with col2:
                            st.write(f"**Category:** {t.get('category')}")
                            st.write(f"**Priority:** {t.get('priority')}")
                            st.write(f"**Status:** `{t.get('status')}`")
                            st.write(f"**Created:** {t.get('created_at')}")

                        st.write("**Description:**")
                        st.info(t.get("description"))


# -----------------------------------------------------------------------------
# 5. Update Ticket Page
# -----------------------------------------------------------------------------
elif menu == "Update Ticket":
    st.markdown('<div class="main-title">✏️ Update Ticket Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Change status between Open, In Progress, and Resolved</div>', unsafe_allow_html=True)

    ticket_id_input = st.text_input("Ticket ID *", placeholder="Enter 24-character Ticket ID")
    new_status = st.selectbox("New Status *", ["Open", "In Progress", "Resolved"])

    if st.button("Update Status", use_container_width=True):
        if not ticket_id_input.strip():
            st.error("⚠️ Please provide a valid Ticket ID.")
        else:
            payload = {"status": new_status}
            success, response_data = fetch_api(f"/tickets/{ticket_id_input.strip()}", method="PUT", data=payload)
            if success:
                st.success(f"✅ Ticket `{ticket_id_input}` updated successfully to **{new_status}**!")
                st.json(response_data)
            else:
                st.error(f"❌ {response_data['detail']}")


# -----------------------------------------------------------------------------
# 6. Delete Ticket Page
# -----------------------------------------------------------------------------
elif menu == "Delete Ticket":
    st.markdown('<div class="main-title">🗑️ Delete Ticket</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Permanently remove a ticket using its ID</div>', unsafe_allow_html=True)

    ticket_id_to_delete = st.text_input("Ticket ID to Delete *", placeholder="Enter 24-character Ticket ID")

    if st.button("Delete Ticket", type="primary", use_container_width=True):
        if not ticket_id_to_delete.strip():
            st.error("⚠️ Please enter a Ticket ID.")
        else:
            success, response_data = fetch_api(f"/tickets/{ticket_id_to_delete.strip()}", method="DELETE")
            if success:
                st.success(f"✅ {response_data.get('message', 'Ticket deleted successfully.')}")
            else:
                st.error(f"❌ {response_data['detail']}")
