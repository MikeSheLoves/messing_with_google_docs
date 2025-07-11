import os.path, streamlit as st
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

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
            # Build the credentials dict from st.secrets
            creds_dict = {
                "installed": dict(st.secrets["installed"])
            }

            flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token locally (Streamlit Cloud won’t persist this)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

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
