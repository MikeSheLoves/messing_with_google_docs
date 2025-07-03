import os.path

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
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("/home/myriad01/PycharmProjects/messing_with_google_docs/google_suite/token.json"):
      creds = Credentials.from_authorized_user_file("/home/myriad01/PycharmProjects/messing_with_google_docs/google_suite/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          "/home/myriad01/PycharmProjects/messing_with_google_docs/google_suite/credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())

    # print("Authentication successful.")
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
