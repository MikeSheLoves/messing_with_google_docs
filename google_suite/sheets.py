from google_suite.google_oauth2 import GoogleStack

class Sheets(GoogleStack):
    def __init__(self):
        super().__init__()
        self.sheets_service = self.build_sheets_service()