from google_suite.google_oauth2 import GoogleStack

class Docs(GoogleStack):
    def __init__(self):
        super().__init__()
        self.docs_service = self.build_docs_service()
