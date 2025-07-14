import os.path, streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]

class GoogleStack:
  def __init__(self):
    self.creds = self.google_authenticate()


  def google_authenticate(self):
    creds = None

    # Handle token.json if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no (valid) credentials, go through flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_dict = {"installed": dict(st.secrets["installed"])}
            flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt='consent')

            st.markdown("### Step 1: Authorize")
            st.markdown(f"[Click here to authorize access]({auth_url})")

            auth_code = st.text_input("Step 2: Paste the authorization code below:")

            if auth_code:
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                st.success("✅ Authentication complete!")

                # Optional: Save to file (will not persist on Streamlit Cloud)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            else:
                st.stop()  # Stop app until auth code is entered

    return creds

  def build_docs_service(self):
    try:
      docs_service = build("docs", "v1", credentials=self.creds)
      return docs_service
    except HttpError as err:
      raise err


  def build_drive_service(self):
    try:
      drive_service = build("drive", "v3", credentials=self.creds)
      return drive_service
    except HttpError as error:
      raise error


  def build_sheets_service(self):
    try:
      sheets_service = build("sheets", "v4", credentials=self.creds)
      return sheets_service
    except HttpError as err:
      raise err
