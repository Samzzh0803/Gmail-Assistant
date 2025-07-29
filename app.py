import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    creds = None

    # Load saved credentials if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, log in and save new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("gmail-api-sameer.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Connect to Gmail API
        service = build("gmail", "v1", credentials=creds)


        #IMPLEMENTATION STARTS HERE.
        # Step 1: Get the 5 most recent messages from INBOX
        results = service.users().messages().list(userId='me', q='category:primary', maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No recent messages.")
        else:
            print("\n📥 Most Recent 5 Emails:\n")
            for msg in messages:
                msg_id = msg['id']
                msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                snippet = msg_data.get('snippet', '')

                print(f"From: {sender}")
                print(f"Subject: {subject}")
                print(f"Snippet: {snippet}")
                print("-" * 50)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
