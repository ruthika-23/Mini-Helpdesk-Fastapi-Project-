"""
Train ML Model for Ticket Priority Classification using a Synthetic Dataset.
Classifies customer complaint tickets into High, Medium, or Low priority.
"""

import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# -----------------------------------------------------------------------------
# 1. Comprehensive Synthetic Dataset for Helpdesk Tickets
# -----------------------------------------------------------------------------
SYNTHETIC_DATA = [
    # --- HIGH PRIORITY (Outages, crashes, security, payment, urgent blockers, data loss) ---
    ("Production server is down completely and users cannot access the portal", "High"),
    ("Critical database crash: Connection timeout on primary cluster", "High"),
    ("Payment gateway is failing, customers cannot checkout or purchase orders", "High"),
    ("Potential security breach detected: Unauthorized root logins from unknown IP", "High"),
    ("Data loss incident: Recent user transactions disappeared from database", "High"),
    ("Complete system outage affecting all European users", "High"),
    ("Ransomware or malware detected on the internal file server", "High"),
    ("Zero-day vulnerability discovered in authentication middleware", "High"),
    ("SSL certificate expired, main domain is completely inaccessible with privacy error", "High"),
    ("Memory leak causing production containers to crash in an endless loop", "High"),
    ("Customers are being double-charged during payment processing", "High"),
    ("Total service disruption, API returning 500 Internal Server Error for all requests", "High"),
    ("Urgent: CEO account compromised and sending phishing emails", "High"),
    ("Data leak: Customer personal details are publicly visible on search index", "High"),
    ("Database replication lag exceeding 10 hours, risking heavy data corruption", "High"),
    ("Core payment API throwing 502 Bad Gateway across all storefronts", "High"),
    ("Urgent critical bug: Entire checkout flow is frozen on submit button", "High"),
    ("All user sessions terminated and nobody can log in including admins", "High"),
    ("Firewall rule misconfiguration blocked all inbound enterprise traffic", "High"),
    ("Disaster recovery failed during backup restoration", "High"),
    ("Critical safety alert: Billing webhook is deleting active customer subscriptions", "High"),
    ("Primary storage volume reached 100% capacity, all write operations failing", "High"),
    ("Severe vulnerability in JWT verification allows token forgery", "High"),
    ("Production cluster nodes are unresponsive, CPU pegged at 100%", "High"),
    ("Urgent: Mobile app crashes immediately upon launch for all iOS users", "High"),
    ("Emergency: Live webinar platform down 10 minutes before global keynote", "High"),
    ("Credit card processing halted by processor due to webhook failure", "High"),
    ("Critical data pipeline crashed, real-time fraud detection is offline", "High"),
    ("Customer records accidentally dropped during database migration", "High"),
    ("DNS propagation error took down all regional subdomains", "High"),
    ("Major outage: Cloud provider network partition severed microservices", "High"),
    ("Critical security alert: SQL injection detected in search endpoint", "High"),
    ("All incoming webhooks failing, orders not being fulfilled", "High"),
    ("Urgent: Core authentication service throwing 503 unavailable", "High"),
    ("Security alert: Suspicious bulk export of sensitive customer records", "High"),
    ("Cannot process credit card payments, checkout fails immediately", "High"),
    ("Immediate action required: Whole website is throwing 500 error", "High"),
    ("Critical: Database corrupted and user data missing", "High"),
    ("Urgent outage: Backend servers completely offline", "High"),
    ("Customer billing compromised, unauthorized charges occurring", "High"),
    ("Server crash in production environment", "High"),
    ("API gateway down, all services inaccessible", "High"),
    ("Emergency fix needed: User login broken for all accounts", "High"),
    ("Severe security flaw: sensitive passwords exposed in plaintext", "High"),
    ("Critical bug causing application to crash on startup", "High"),

    # --- MEDIUM PRIORITY (Performance degradation, non-blocking bugs, UI alignment, sync issues) ---
    ("Slow page load times on the analytics dashboard during peak hours", "Medium"),
    ("Password reset email is delayed by 15 minutes", "Medium"),
    ("Export to CSV is missing the last two transaction columns", "Medium"),
    ("Search filters are not resetting when clicking the clear button", "Medium"),
    ("Intermittent 404 error when clicking certain user profile avatars", "Medium"),
    ("Notification bell icon shows incorrect unread count badge", "Medium"),
    ("Report generation takes more than 3 minutes to complete", "Medium"),
    ("Users cannot upload profile pictures larger than 2MB despite 10MB limit", "Medium"),
    ("Weekly summary email contains duplicate entries for some users", "Medium"),
    ("Date picker calendar widget behaves inconsistently in Safari browser", "Medium"),
    ("Pagination on the ticket list page skips page numbers when filtered", "Medium"),
    ("Invoice PDF download has misaligned table borders and text wrapping issues", "Medium"),
    ("Mobile responsive layout breaks on iPad landscape view", "Medium"),
    ("Draft messages are not auto-saving properly when switching tabs", "Medium"),
    ("Webhook delivery retry logic attempts 5 times instead of configured 3", "Medium"),
    ("Sorting by column header is not working for the 'Assigned To' column", "Medium"),
    ("Minor synchronization delay between desktop client and mobile application", "Medium"),
    ("User settings page takes 5 seconds to persist updated notification preferences", "Medium"),
    ("Unable to change default currency in workspace settings", "Medium"),
    ("Chart tooltips display truncated numbers for large revenue amounts", "Medium"),
    ("Two-factor authentication SMS takes longer than usual to arrive", "Medium"),
    ("Auto-complete suggestions are sluggish when typing customer names", "Medium"),
    ("Session timeout dialog does not extend session when 'Stay logged in' is clicked", "Medium"),
    ("Batch delete button is disabled even when multiple rows are checked", "Medium"),
    ("API rate limit header not being sent on responses", "Medium"),
    ("Attachment preview thumbnail fails to render for certain PDF files", "Medium"),
    ("Incorrect timestamp displayed for comments in daylight savings timezone", "Medium"),
    ("Sub-tasks ordering does not persist after dragging and dropping", "Medium"),
    ("Language translation for French is incomplete on billing invoice", "Medium"),
    ("User invitation link shows expired message before 24 hours elapsed", "Medium"),
    ("Bulk status update on tickets only updates first 10 items instead of 50", "Medium"),
    ("Dark mode toggle requires page reload to take full effect", "Medium"),
    ("Google Calendar integration syncs events with a 30-minute delay", "Medium"),
    ("Slack notification bot disconnects intermittently once every week", "Medium"),
    ("Search autocomplete returns results from archived projects", "Medium"),
    ("App is running noticeably slower than usual on mobile browsers", "Medium"),
    ("Filter by date range does not show recent yesterday results", "Medium"),
    ("Audio playback in browser has occasional stuttering or lag", "Medium"),
    ("Profile page loads slowly after updating profile photo", "Medium"),
    ("Sync between devices has a noticeable 15 second delay", "Medium"),
    ("Some table columns are cut off on low resolution screens", "Medium"),
    ("Form validation error message disappears too quickly", "Medium"),
    ("Exported Excel file formatting is slightly distorted", "Medium"),
    ("User role permissions not refreshing without page reload", "Medium"),
    ("Email notification arrives 10 minutes late after ticket creation", "Medium"),

    # --- LOW PRIORITY (Cosmetic changes, typos, questions, feedback, minor preferences) ---
    ("Typo found on the 'About Us' company description page", "Low"),
    ("Feature request: Can you add a dark mode theme option?", "Low"),
    ("General inquiry about annual subscription pricing and volume discounts", "Low"),
    ("Documentation guide has a broken link to the v1 legacy API docs", "Low"),
    ("Would love to see more emoji reactions available in comment threads", "Low"),
    ("Minor color discrepancy between the navbar logo and footer logo", "Low"),
    ("Inquiry: How do I change the display name of my organization?", "Low"),
    ("Suggestion: Add keyboard shortcut for switching between open tabs", "Low"),
    ("Footer copyright year still says 2024 instead of the current year", "Low"),
    ("Question: Is there a public roadmap for upcoming third-party integrations?", "Low"),
    ("Spelling mistake in onboarding welcome email step 3", "Low"),
    ("Request for additional font choices in the document editor", "Low"),
    ("Can I get an invoice receipt sent to a secondary accounting email?", "Low"),
    ("Suggestion: Allow reordering dashboard metric widgets by preference", "Low"),
    ("Compliment: Loving the new update! Just wanted to share positive feedback", "Low"),
    ("How do I unsubscribe from marketing promotional newsletters?", "Low"),
    ("The tooltip text on the help icon has a minor grammatical typo", "Low"),
    ("Inquiry regarding enterprise SLA options and response time guarantees", "Low"),
    ("Suggestion to make the logo in the top left corner slightly bigger", "Low"),
    ("Is there any community forum or Discord server for developers?", "Low"),
    ("Add option to export charts as PNG images rather than only SVG", "Low"),
    ("Clarification needed on data retention policy for deleted accounts", "Low"),
    ("Can we customize the welcome greeting text on user login?", "Low"),
    ("Button hover color is slightly darker than Figma brand design spec", "Low"),
    ("Inquiry: Does your platform support Portuguese language localization?", "Low"),
    ("Feedback: Would be nice to have sound effects when tickets are resolved", "Low"),
    ("Request for webinar recordings link from last month's session", "Low"),
    ("Typo in FAQ section under 'How to invite team members'", "Low"),
    ("Can we add custom badges or avatars for internal team champions?", "Low"),
    ("Question: How do I download my personal profile data archive?", "Low"),
    ("The social media link for Twitter points to the old handle", "Low"),
    ("Suggestion to add breadcrumb navigation on nested settings subpages", "Low"),
    ("General feedback: The contrast on disabled form inputs could be slightly higher", "Low"),
    ("Inquiry about API documentation examples in Ruby or Go", "Low"),
    ("Question about best practices for organizing tags across teams", "Low"),
    ("Grammar correction needed on terms of service section 4", "Low"),
    ("Can you change the button text from Submit to Send?", "Low"),
    ("Cosmetic alignment: Footer links could have a little more padding", "Low"),
    ("Feature request: Ability to star favorite projects", "Low"),
    ("General question about pricing plan features and differences", "Low"),
    ("Nice work on the recent release! Praise to the support team", "Low"),
    ("Request for product brochure and presentation slides", "Low"),
    ("Small spelling error in privacy notice paragraph 2", "Low"),
    ("Suggestion: Add keyboard navigation to dropdown menus", "Low"),
    ("Inquiry regarding sales contact number for partnership inquiries", "Low"),
]


def train_and_save_model(model_path: str = "priority_model.joblib"):
    """
    Train a text classification pipeline on synthetic helpdesk data and save to disk.
    """
    texts = [item[0] for item in SYNTHETIC_DATA]
    labels = [item[1] for item in SYNTHETIC_DATA]

    # Split dataset for training and validation
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # Build Pipeline: TF-IDF vectorizer + Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            min_df=1,
            sublinear_tf=True
        )),
        ('clf', LogisticRegression(
            C=2.0,
            class_weight='balanced',
            max_iter=1000,
            random_state=42
        ))
    ])

    print("Training ML model on synthetic ticket dataset...")
    pipeline.fit(X_train, y_train)

    # Evaluate model
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Validation Accuracy: {acc * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    # Fit on all synthetic data for final production model
    pipeline.fit(texts, labels)

    # Save trained model pipeline
    joblib.dump(pipeline, model_path)
    print(f"Successfully trained and saved model to '{model_path}'")
    return pipeline


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "priority_model.joblib")
    train_and_save_model(output_path)

