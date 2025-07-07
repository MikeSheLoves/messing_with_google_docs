from google_suite.google_oauth2 import GoogleStack
import json

TEST_DATA = {'customer_name': 'Tamlin', 'date': '2025-07-07', 'vat_inclusive': True, 'must_show_vat': True, 'vat_perc': 15, 'description': ['Kitchen cupboards in Supawood and Melamine as per customer’s reference image and spec’s, measuring at 2,6m', 'Reception Desk to measure 2,2m L in Supawood and Meranti as per customer’s reference image, with a gloss finish'], 'units': [1, 1], 'price_per_unit': [12500.0, 11500.0], 'price_of_item': [12500.0, 11500.0]}
TEST_DOC_ID = "1YLg7WanvnMFw2WbWEqbv6P2UZNAlRL54igOh8-LvpFU"

class Docs(GoogleStack):
    def __init__(self, docId, data):
        super().__init__()
        self.doc_Id = docId
        self.data = data
        self.docs_service = self.build_docs_service()
        self.doc_obj = self.docs_service.documents()
        self.doc_dict = self.docs_service.documents().get(documentId=self.doc_Id).execute()
        self.table_rows = self.doc_dict.get('body').get("content")[3].get("table").get("tableRows")

    def update_doc(self):
        self.doc_obj = self.docs_service.documents()
        self.doc_dict = self.docs_service.documents().get(documentId=self.doc_Id).execute()
        self.table_rows = self.doc_dict.get('body').get("content")[3].get("table").get("tableRows")

    def insert_rows(self, num_of_rows):
        request_body = []
        for num in range(num_of_rows):
            row_request = {
                "insertTableRow": {
                    "tableCellLocation": {
                        "tableStartLocation": {
                            "index": 27,
                        },
                        "rowIndex": num,
                        "columnIndex": 1
                    },
                    "insertBelow": "true",
                }
            }
            request_body.append(row_request)

        self.doc_obj.batchUpdate(documentId=self.doc_Id, body={"requests": request_body}).execute()

    def populate_rows(self, num_of_rows):
        request_body = []
        requirements = ('description', 'units','price_per_unit', 'price_of_item')
        items = [(key, value) for (key, value) in self.data.items() if key in requirements]
        self.update_doc()

        for row in range(num_of_rows - 1, -1, -1):

            for column in range(3, -1, -1):
                start_index = self.table_rows[row + 1]["tableCells"][column]["startIndex"]
                text = str(items[column][1][row])
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
                        },
                        "fields": "bold",
                    }
                }

                request_body.append(insert_request)
                request_body.append(update_text_request)

        self.doc_obj.batchUpdate(documentId=self.doc_Id, body={"requests": request_body}).execute()


    def get_indexes(self):
        pass

    # def print_doc(self):
    #     self.update_doc()
    #     return json.dumps(self.doc_dict, indent=2)

# test = Docs(docId=TEST_DOC_ID, data=TEST_DATA)
# test.insert_rows(len(TEST_DATA["description"]))
# test.populate_rows(len(TEST_DATA["description"]))
