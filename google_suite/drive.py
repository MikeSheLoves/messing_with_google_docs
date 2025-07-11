from google_suite.google_oauth2 import GoogleStack
from random import choice
from dotenv import load_dotenv
import os.path

load_dotenv(dotenv_path=".venv/.env")

class Drive(GoogleStack):
    def __init__(self, data):
        super().__init__()
        self.drive_service = self.build_drive_service()
        self.data = data
        self.invoice_num = ""
        self.document_type = self.data["document_type"]

    def get_file_id(self):
        if self.data["document_type"] == "Invoice":
            return os.environ["INVOICE_TEMPLATE_FILE_ID"]
        else:
            return os.environ["QUOTATION_TEMPLATE_FILE_ID"]

    def create_invoice_num(self):
        short_date = f"{self.data["date"][2:]}"
        invoice_num = f"{self.data["customer_name"][0].upper()}{choice(self.data["customer_name"]).upper()}{short_date}"
        self.invoice_num = invoice_num
        return invoice_num

    def get_template_copy(self):
        file_id = self.get_file_id()
        document_title = f"{self.data["document_type"]} {self.invoice_num} for {self.data["customer_name"]} ({self.data["date"]})"
        request_body = {
            "name": document_title,
        }
        return self.drive_service.files().copy(fileId=file_id, body=request_body).execute()

# test = Drive(data={'customer_name': 'Tom', 'date': '2025-07-10', 'vat_inclusive': True, 'must_show_vat': True, 'vat_perc': 15, 'description': ['Apples.'], 'units': [2], 'price_per_unit': [50.0], 'price_of_item': [100.0], 'deposit': 0.0, 'discount': 0.0, 'document_type': 'Invoice'})
# print(test.get_file_id())