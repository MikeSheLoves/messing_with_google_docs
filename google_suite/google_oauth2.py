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


  import streamlit as st
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import os
import requests

SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]

def google_authenticate():
    # Load credentials from Streamlit secrets
    creds_dict = {"web": dict(st.secrets["web"])}

    # Streamlit-specific URL (your deployed Cloud Run URL)
    redirect_uri = st.secrets["web"]["redirect_uris"][0]
    flow = Flow.from_client_config(
        creds_dict,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    # Handle authorization callback
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        auth_code = query_params["code"][0]
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        st.session_state["google_creds"] = creds
        st.success("✅ Authenticated with Google successfully!")
        return creds

    # If not authorized, redirect to Google's auth page
    if "google_creds" not in st.session_state:
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
        st.markdown(f"🔐 [Click here to authenticate with Google Docs]({auth_url})")
        st.stop()

    return st.session_state["google_creds"]

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
