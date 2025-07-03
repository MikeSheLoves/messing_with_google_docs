from genaillm import InvoiceLLM
from google_suite.drive import Drive
from google_suite.docs import Docs
from user_input_exception import UserInputError
from datetime import datetime
g_llm = InvoiceLLM()

#TODO 1: Ask the user what they want to put in their invoice
user_input = ""

while not user_input:
    user_input = input("Type out the contents of the invoice:\n")

    # TODO 2: Process and validate the user input
    if user_input.lower() == "exit":
        exit()

    data = g_llm.arrange_data(user_input)

    if isinstance(data, UserInputError):
        print(data)
        user_input = ""

#TODO 3: Make a copy of the invoice template
gd = Drive()

if data["date"] is None:
    data["date"] = datetime.today().strftime("%Y-%m-%d")

customer_invoice_data = gd.get_template_copy(invoice_dict=data)
customer_invoice_id = customer_invoice_data["id"]

#TODO 4: Edit the content of the invoice copy
gdocs = Docs()
#TODO 5: Add the totals to the invoice copy

#TODO 6: Save the order details to Google sheets

#TODO 7: Send to the user as PDF via email



