from google_suite.google_oauth2 import GoogleStack
from googleapiclient.errors import HttpError
from enum import Enum
from datetime import datetime

CURRENCY = "R" #ZAR

class Docs(GoogleStack):
    def __init__(self, docId, data, invnum):
        super().__init__()
        self.doc_Id = docId
        self.data = data
        self.invoice_num = invnum
        self.docs_service = self.build_docs_service()
        self.doc_obj = self.docs_service.documents()
        self.doc_dict = self.docs_service.documents().get(documentId=self.doc_Id).execute()
        self.table_content = {}
        self.table_rows = []
        self.get_table_rows()
        self.num_of_rows = 0

    def get_table_rows(self):
        for item in self.doc_dict.get('body').get("content"):
            if "table" in item:
                self.table_content = item
                self.table_rows = item.get("table").get("tableRows")

    def update_doc(self):
        self.doc_obj = self.docs_service.documents()
        self.doc_dict = self.docs_service.documents().get(documentId=self.doc_Id).execute()
        self.get_table_rows()

    def update_invoice_details(self):
        replace_requests = [
            {
                "replaceAllText": {
                    "containsText": {
                        "text": "{{CustomerName}}",
                        "matchCase": True,
                    },
                    "replaceText": self.data["customer_name"],
                }
            },
            {
                "replaceAllText": {
                    "containsText": {
                        "text": "{{Date}}",
                        "matchCase": True,
                    },
                    "replaceText": self.data["date"],
                }
            },
            {
                "replaceAllText": {
                    "containsText": {
                        "text": "{{InvoiceNum}}",
                        "matchCase": True,
                    },
                    "replaceText": self.invoice_num,
                }
            }
        ]

        self.modify_doc(requests=replace_requests)

    def modify_doc(self, requests):
        try:
            self.doc_obj.batchUpdate(documentId=self.doc_Id, body={"requests": requests}).execute()
        except HttpError as error:
            status = error.resp.status
            reason = error.error_details if hasattr(error, "error_details") else error.reason

            if status == 401:
                print("Unauthorized. Token may be expired or revoked.")
            elif status == 403:
                print("Access forbidden. Check your API scopes and permissions.")
            elif status == 404:
                print("Not found. The requested resource doesn't exist.")
            elif status == 429:
                print("Rate limit exceeded.")
            elif 500 <= status < 600:
                print("Server error. Try again later.")
            elif status:
                print(f"Unhandled HTTP error {status}: {reason}")

            with open("error.log", "a") as log:
                log.write(f"[{status}] {error} {datetime.today().strftime("%Y-%m-%d")}\n")

    def insert_rows(self):
        request_body = []
        self.num_of_rows = len(self.data["description"])
        table_start = self.table_content["startIndex"]

        for num in range(self.num_of_rows):
            row_request = {
                "insertTableRow": {
                    "tableCellLocation": {
                        "tableStartLocation": {
                            "index": table_start,
                        },
                        "rowIndex": num,
                        "columnIndex": 1
                    },
                    "insertBelow": "true",
                }
            }
            request_body.append(row_request)

        self.modify_doc(requests=request_body)

    def populate_rows(self):
        request_body = []
        requirements = ('description', 'units','price_per_unit', 'price_of_item')
        items = [(key, value) for (key, value) in self.data.items() if key in requirements]
        self.update_invoice_details()
        self.update_doc()

        #Populates the cells from the bottom right to the top left
        for row in range(self.num_of_rows - 1, -1, -1):

            for column in range(3, -1, -1):
                start_index = self.table_rows[row + 1]["tableCells"][column]["startIndex"]

                store = items[column][1][row]
                if isinstance(store, float):
                    text = f"{CURRENCY}{store:.2f}"
                else:
                    text = str(store)

                end_index = start_index + len(text) + 1
                insert_request = {
                        "insertText": {
                            "location": {
                                "index": start_index + 1
                            },
                            "text": text
                        }
                    }

                update_text_request = {
                    "updateTextStyle": {
                        "range": {"startIndex": start_index, "endIndex": end_index},
                        "textStyle": {
                            "bold": False,
                            "underline": False,
                        },
                        "fields": "bold, underline",
                    }
                }

                request_body.append(insert_request)
                request_body.append(update_text_request)

        self.modify_doc(requests=request_body)

    def include_totals(self, totals_set):
        request_body = []
        self.update_doc()
        totals_rows_num = len(self.table_rows)
        last_num_of_list = totals_rows_num -1

        class Totals(Enum):
            total_due = last_num_of_list
            nett = last_num_of_list - 1
            vat = last_num_of_list -2
            subtotal = last_num_of_list - 3

        #Populates cells from the bottom to the top
        for row in range(last_num_of_list, totals_rows_num - 5, -1):
            placeholder = self.table_rows[row]["tableCells"][3]["content"][0]["paragraph"]["elements"][0]["textRun"]["content"]
            field = Totals(row)
            text = CURRENCY + totals_set[field.name]

            replace_request = {
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True,
                    },
                    "replaceText": text,
                }
            }

            request_body.append(replace_request)

        self.modify_doc(requests=request_body)
