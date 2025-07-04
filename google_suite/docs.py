from google_suite.google_oauth2 import GoogleStack
import json

class Docs(GoogleStack):
    def __init__(self, docId):
        super().__init__()
        self.doc_Id = docId
        self.docs_service = self.build_docs_service()
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
                            "index": 28,
                        },
                        "rowIndex": num,
                        "columnIndex": 1
                    },
                    "insertBelow": "true",
                }
            }
            request_body.append(row_request)

        result = self.doc_obj.batchUpdate(documentId=self.doc_Id, body={"requests": request_body}).execute()
        return result

    def get_indexes(self):
        pass

    def print_doc(self):
        return json.dumps(self.doc_dict, indent=2)

test = Docs(docId="1RTqPX8gPW6glyGbNsCWg78plmGmW6eANTScrtdAU7ls")
print(test.insert_rows(4))