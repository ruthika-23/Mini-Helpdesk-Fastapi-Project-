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
    .priority-badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        font-size: 1.1rem;
        border: 1px solid #f87171;
    }
    .priority-badge-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        font-size: 1.1rem;
        border: 1px solid #fcd34d;
    }
    .priority-badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        font-size: 1.1rem;
        border: 1px solid #86efac;
    }
    .prediction-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
        "Prediction",
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
    st.markdown('<div class="sub-title">Submit a new inquiry or issue for resolution (Priority is predicted by ML)</div>', unsafe_allow_html=True)

    with st.form("create_ticket_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("User Name *", placeholder="e.g. Ruthika")
            category = st.selectbox("Category *", ["Technical", "Billing", "Account", "General"])
        with col2:
            email = st.text_input("Email Address *", placeholder="e.g. user@example.com")
            st.info("🤖 **AI Priority Auto-Detection**: Priority will be automatically evaluated from your issue description by the trained ML model.")

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
                    "category": category
                }
                success, response_data = fetch_api("/tickets", method="POST", data=payload)
                if success:
                    predicted_p = response_data.get("priority", "N/A")
                    st.success(f"✅ Ticket created successfully! Assigned ID: `{response_data.get('id')}` | 🤖 AI Assigned Priority: **{predicted_p}**")
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
# 5. ML Priority Prediction Page
# -----------------------------------------------------------------------------
elif menu == "Prediction":
    st.markdown('<div class="main-title">🤖 AI Ticket Priority Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Predict whether customer complaints are <strong>High</strong>, <strong>Medium</strong>, or <strong>Low</strong> priority using Machine Learning</div>', unsafe_allow_html=True)

    tab_by_id, tab_custom = st.tabs(["🎫 Predict by Ticket ID", "🧪 Test Complaint Text Directly"])

    with tab_by_id:
        st.markdown("#### 🎫 Analyze & Predict Ticket Priority")
        st.caption("Provide a Ticket ID to retrieve its complaint text (title & description) and run the trained ML model.")

        # Fetch all tickets to provide a convenient dropdown helper
        t_ok, tickets_list = fetch_api("/tickets")
        ticket_map = {}
        if t_ok and tickets_list:
            for t in tickets_list:
                label = f"{t.get('id')} — {t.get('title')[:35]} (Current: {t.get('priority')})"
                ticket_map[label] = t.get('id')

        col_id_in, col_id_dd = st.columns([1.5, 1.5])
        with col_id_in:
            manual_id = st.text_input("Enter 24-character Ticket ID *", placeholder="e.g. 660fe45b... or paste ID here")
        with col_id_dd:
            selected_label = st.selectbox(
                "Quick Select from Existing Tickets",
                ["-- Choose an existing ticket --"] + list(ticket_map.keys())
            )
            if selected_label != "-- Choose an existing ticket --":
                manual_id = ticket_map[selected_label]

        predict_clicked = st.button("🔮 Predict Priority from Complaint", type="primary", use_container_width=True)

        if predict_clicked or (manual_id and len(manual_id.strip()) == 24):
            if not manual_id.strip():
                st.warning("⚠️ Please enter or select a Ticket ID.")
            else:
                tid = manual_id.strip()
                with st.spinner("Fetching ticket and running ML priority prediction..."):
                    # 1. Fetch ticket details
                    ticket_ok, ticket_info = fetch_api(f"/tickets/{tid}")

                    if not ticket_ok:
                        st.error(f"❌ Failed to find ticket: {ticket_info['detail']}")
                    else:
                        # 2. Call prediction API
                        pred_ok, pred_info = fetch_api(f"/tickets/{tid}/predict-priority", method="POST")

                        if not pred_ok:
                            st.error(f"❌ Prediction service error: {pred_info['detail']}")
                        else:
                            predicted_p = pred_info.get("predicted_priority", "Medium")
                            conf = pred_info.get("confidence", 0.0)
                            probs = pred_info.get("probabilities", {})

                            st.markdown("---")

                            # Display Ticket Context
                            with st.expander(f"📋 Ticket: {ticket_info.get('title')}", expanded=True):
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.write(f"**Ticket ID:** `{ticket_info.get('id')}`")
                                    st.write(f"**Submitted By:** {ticket_info.get('user_name')}")
                                with c2:
                                    st.write(f"**Category:** {ticket_info.get('category')}")
                                    st.write(f"**Current Database Priority:** `{ticket_info.get('priority')}`")
                                with c3:
                                    st.write(f"**Status:** `{ticket_info.get('status')}`")
                                    st.write(f"**Created At:** {ticket_info.get('created_at')}")

                                st.markdown("**Ticket Title:**")
                                st.write(ticket_info.get("title"))
                                st.markdown("**Customer Complaint / Issue Description:**")
                                st.info(ticket_info.get("description"))

                            # ML Prediction Result Presentation
                            st.markdown("### 🎯 Machine Learning Evaluation")
                            col_pred_card, col_prob_card = st.columns([1.2, 1.8])

                            with col_pred_card:
                                p_badge_class = f"priority-badge-{predicted_p.lower()}"
                                icon = "🚨" if predicted_p == "High" else ("🟡" if predicted_p == "Medium" else "🟢")
                                st.markdown(f"""
                                <div class="prediction-box">
                                    <div style="font-size: 0.85rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">
                                        ML Predicted Priority
                                    </div>
                                    <div class="{p_badge_class}">
                                        {icon} {predicted_p} Priority
                                    </div>
                                    <div style="margin-top: 14px; font-size: 1.05rem; color: #334155;">
                                        Confidence: <strong>{conf * 100:.1f}%</strong>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_prob_card:
                                st.markdown("""
                                <div class="prediction-box">
                                    <div style="font-size: 0.85rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                                        Confidence Distribution
                                    </div>
                                """, unsafe_allow_html=True)
                                h_prob = probs.get("High", 0.0)
                                m_prob = probs.get("Medium", 0.0)
                                l_prob = probs.get("Low", 0.0)

                                st.write(f"🚨 **High Priority:** `{h_prob * 100:.1f}%`")
                                st.progress(min(max(float(h_prob), 0.0), 1.0))

                                st.write(f"🟡 **Medium Priority:** `{m_prob * 100:.1f}%`")
                                st.progress(min(max(float(m_prob), 0.0), 1.0))

                                st.write(f"🟢 **Low Priority:** `{l_prob * 100:.1f}%`")
                                st.progress(min(max(float(l_prob), 0.0), 1.0))
                                st.markdown("</div>", unsafe_allow_html=True)

                            # Quick action: Update Database Priority to Predicted Priority
                            st.markdown(" ")
                            if ticket_info.get("priority") != predicted_p:
                                if st.button(f"💾 Update Ticket Priority to '{predicted_p}' in Database", use_container_width=True):
                                    up_ok, up_data = fetch_api(f"/tickets/{tid}", method="PUT", data={"priority": predicted_p})
                                    if up_ok:
                                        st.success(f"🎉 Updated Ticket `{tid}` priority to **{predicted_p}** successfully in MongoDB!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to update priority: {up_data['detail']}")
                            else:
                                st.success(f"✔️ Ticket priority in database is already aligned with the ML prediction (**{predicted_p}**).")

    with tab_custom:
        st.markdown("#### 🧪 Test Complaint Text Directly")
        st.caption("Enter any custom problem description or complaint to see how the ML model categorizes its priority.")

        custom_text = st.text_area(
            "Customer Complaint / Issue Description",
            placeholder="e.g. Critical production server outage! All users getting 500 error and database is locked...",
            height=120
        )

        if st.button("🔮 Classify Custom Complaint", type="primary"):
            if not custom_text.strip():
                st.warning("Please enter some complaint text to analyze.")
            else:
                with st.spinner("Analyzing complaint..."):
                    c_ok, c_res = fetch_api("/predict-priority", method="POST", data={"text": custom_text.strip()})
                    if not c_ok:
                        st.error(f"❌ Prediction error: {c_res['detail']}")
                    else:
                        c_pred = c_res.get("predicted_priority", "Medium")
                        c_conf = c_res.get("confidence", 0.0)
                        c_probs = c_res.get("probabilities", {})

                        st.markdown("---")
                        col_c1, col_c2 = st.columns([1.2, 1.8])
                        with col_c1:
                            c_badge = f"priority-badge-{c_pred.lower()}"
                            c_icon = "🚨" if c_pred == "High" else ("🟡" if c_pred == "Medium" else "🟢")
                            st.markdown(f"""
                            <div class="prediction-box">
                                <div style="font-size: 0.85rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">
                                    Predicted Priority
                                </div>
                                <div class="{c_badge}">
                                    {c_icon} {c_pred} Priority
                                </div>
                                <div style="margin-top: 14px; font-size: 1.05rem; color: #334155;">
                                    Confidence: <strong>{c_conf * 100:.1f}%</strong>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_c2:
                            st.markdown("""
                            <div class="prediction-box">
                                <div style="font-size: 0.85rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                                    Probability Distribution
                                </div>
                            """, unsafe_allow_html=True)
                            for cls_name, val in c_probs.items():
                                st.write(f"**{cls_name}:** `{val * 100:.1f}%`")
                                st.progress(float(val))
                            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. Update Ticket Page
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
