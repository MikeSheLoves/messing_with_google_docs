from google_suite.google_oauth2 import GoogleStack
from googleapiclient.errors import HttpError
from enum import Enum
import json

TEST_DATA = {'customer_name': 'Susan Storm', 'date': '2025-07-08', 'vat_inclusive': True, 'must_show_vat': True, 'vat_perc': 15, 'description': ['Chicken Eggs', 'Ostrich Eggs'], 'units': [45, 21], 'price_per_unit': [0.45, 230.0], 'price_of_item': [20.25, 4830.0]}
TEST_DOC_ID = "11dgqd_QlDLzSvNyEiynmvPoCCIuevNDIp4hVDNF4RQk"


class Docs(GoogleStack):
    def __init__(self, docId, data):
        super().__init__()
        self.doc_Id = docId
        self.data = data
        self.docs_service = self.build_docs_service()
        self.doc_obj = self.docs_service.documents()
        self.doc_dict = self.docs_service.documents().get(documentId=self.doc_Id).execute()
        self.table_rows = self.doc_dict.get('body').get("content")[3].get("table").get("tableRows")
        self.num_of_rows = 0

    def update_doc(self):
        self.doc_obj = self.docs_service.documents()
        self.doc_dict = self.docs_service.documents().get(documentId=self.doc_Id).execute()
        self.table_rows = self.doc_dict.get('body').get("content")[3].get("table").get("tableRows")

    def update_customer_name(self):
        replace_request = {
            "replaceAllText": {
                "containsText": {
                    "text": "{{customerName}}",
                    "matchCase": True,
                },
                "replaceText": self.data["customer_name"],
            }
        }

        self.modify_doc(requests=replace_request)

    def modify_doc(self, requests):
        try:
            # Your API call here
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

            # Optional: log to file
            with open("error.log", "a") as log:
                log.write(f"[{status}] {error}\n")


    def insert_rows(self):
        request_body = []
        self.num_of_rows = len(self.data["description"])

        for num in range(self.num_of_rows):
            row_request = {
                "insertTableRow": {
                    "tableCellLocation": {
                        "tableStartLocation": {
                            "index": 28,
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
        self.update_customer_name()
        self.update_doc()

        for row in range(self.num_of_rows - 1, -1, -1):

            for column in range(3, -1, -1):
                start_index = self.table_rows[row + 1]["tableCells"][column]["startIndex"]

                store = items[column][1][row]
                if isinstance(store, float):
                    text = f"{store:.2f}"
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

        for row in range(last_num_of_list, totals_rows_num - 5, -1):
            placeholder = self.table_rows[row]["tableCells"][3]["content"][0]["paragraph"]["elements"][0]["textRun"]["content"]
            field = Totals(row)
            text = totals_set[field.name]

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

    def print_doc(self):
        self.update_doc()
        return json.dumps(self.doc_dict, indent=2)

# test = Docs(docId=TEST_DOC_ID, data=TEST_DATA)
#
# totals = {
#         "subtotal": "4850.25",
#         "vat": "632.64",
#         "nett": "4217.61",
#         "total_due": "4850.25",
#     }
#
# test.include_totals(totals_set=totals)
