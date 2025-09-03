from __future__ import print_function
import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Use .modify so we can fetch, send, and create drafts
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Token file for Faheem
TOKEN_FILE = "token.json"

def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "gmail-api-sameer.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def fetch_recent_emails(service, max_results=5):
    """Fetch recent emails."""
    try:
        print("📥 Fetching most recent emails...")
        results = service.users().messages().list(
            userId="me", labelIds=["INBOX"], maxResults=max_results
        ).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        for msg in messages:
            msg_detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_detail["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
            print(f"📧 {subject} — from {sender}")

    except HttpError as error:
        print(f"An error occurred: {error}")

def create_message(sender, to, subject, body):
    """Create a properly formatted MIME message."""
    message = MIMEMultipart()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject

    # Attach the email body
    message.attach(MIMEText(body, "plain"))

    # Encode as base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {"raw": raw_message.decode()}

def send_email(service, sender, to, subject, body):
    """Send an email using Gmail API."""
    try:
        print("📤 Sending a new email...")
        message = create_message(sender, to, subject, body)
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"✅ Email sent! Message ID: {sent_message['id']}")
    except HttpError as error:
        print(f"An error occurred while sending: {error}")

def create_draft(service, sender, to, subject, body):
    """Create a draft email."""
    try:
        print("📝 Creating a draft...")
        message = create_message(sender, to, subject, body)
        draft = service.users().drafts().create(
            userId="me", body={"message": message}
        ).execute()
        print(f"✅ Draft created! Draft ID: {draft['id']}")
    except HttpError as error:
        print(f"An error occurred while creating draft: {error}")

if __name__ == "__main__":
    service = authenticate_gmail()

    # Fetch top 5 recent emails
    fetch_recent_emails(service, max_results=5)

    # Example: Send an email
    send_email(
        service,
        sender="samzztrades@gmail.com",      # Replace with your Gmail
        to="muhammadfaheemhaider133@gmail.com",     # Replace with recipient Gmail
        subject="Hello from Gmail API",
        body="This is a test email sent using the Gmail API!"
    )

    # Example: Create a draft
    create_draft(
        service,
        sender="samzztrades@gmail.com",
        to="muhammadfaheemhaider133@gmail.com",
        subject="Draft Test",
        body="This is a saved draft using Gmail API."
    )
