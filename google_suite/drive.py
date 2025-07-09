from google_suite.google_oauth2 import GoogleStack
from random import choice
from dotenv import load_dotenv
import os.path

load_dotenv()

class Drive(GoogleStack):
    def __init__(self, data):
        super().__init__()
        self.drive_service = self.build_drive_service()
        self.data = data
        self.invoice_num = ""

    def get_file_id(self):
        if os.environ["TEMPLATE_FILE_ID"]:
            return os.environ["TEMPLATE_FILE_ID"]

        drive_dict = self.drive_service.files().list().execute()
        files_list = drive_dict["files"]
        for item in files_list:
            if item["name"] == "Invoice Template":
                file_id = item["id"]
        return file_id

    def create_invoice_num(self):
        short_date = f"{self.data["date"][2:]}"
        invoice_num = f"{self.data["customer_name"][0].upper()}{choice(self.data["customer_name"]).upper()}{short_date}"
        self.invoice_num = invoice_num
        return invoice_num

    def get_template_copy(self, invoice_dict):
        file_id = self.get_file_id()
        invoice_title = f"Invoice {self.invoice_num} for {invoice_dict["customer_name"]} ({invoice_dict["date"]})"
        request_body = {
            "name": invoice_title,
        }
        return self.drive_service.files().copy(fileId=file_id, body=request_body).execute()
