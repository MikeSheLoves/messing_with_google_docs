from google_suite.google_oauth2 import GoogleStack
import os.path

class Drive(GoogleStack):
    def __init__(self):
        super().__init__()
        self.drive_service = self.build_drive_service()

    def get_file_id(self):
        if os.path.exists("invoice_template_fileid.txt"):
            with open(file="invoice_template_fileid.txt", mode="r") as file_id_file:
                file_id = file_id_file.read()
            return file_id

        drive_dict = self.drive_service.files().list().execute()
        files_list = drive_dict["files"]
        for item in files_list:
            if item["name"] == "Invoice Template":
                file_id = item["id"]
        with open(file="invoice_template_fileid.txt", mode="w") as file_id_file:
            file_id_file.write(file_id)
        return file_id

    def get_template_copy(self, invoice_dict):
        file_id = self.get_file_id()
        invoice_title = f"Invoice for {invoice_dict["customer_name"]} ({invoice_dict["date"]})"
        request_body = {
            "name": invoice_title,
        }
        return self.drive_service.files().copy(fileId=file_id, body=request_body).execute()

# test = Drive()
# print(test.get_template_copy())