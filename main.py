from genaillm import InvoiceLLM
from google_suite.drive import Drive
from google_suite.docs import Docs
from user_input_exception import UserInputError
from datetime import datetime
from enum import Enum
g_llm = InvoiceLLM()

def calculate_totals(data):
    vat_perc = (data["vat_perc"] / 100) + 1
    subtotal = 0

    for item in range(len(data["description"])):
        subtotal += data["price_of_item"][item]

    vat_amount = subtotal - (subtotal / vat_perc)
    nett_amount = subtotal / vat_perc
    total_due = subtotal

    totals = {
        "subtotal": f"{subtotal:.2f}",
        "vat": f"{vat_amount:.2f}",
        "nett": f"{nett_amount:.2f}",
        "total_due": f"{total_due:.2f}",
    }

    return totals

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
gdr = Drive()

if data["date"] is None:
    data["date"] = datetime.today().strftime("%Y-%m-%d")

customer_invoice_data = gdr.get_template_copy(invoice_dict=data)
customer_invoice_id = customer_invoice_data["id"]

#TODO 4: Edit the content of the invoice copy
gdc = Docs(docId=customer_invoice_id, data=data)
gdc.insert_rows()
gdc.populate_rows()

#TODO 5: Add the totals to the invoice copy
invoice_totals = calculate_totals(data=data)
gdc.include_totals(totals_set=invoice_totals)

#TODO 6: Save the order details to Google sheets

#TODO 7: Send to the user as PDF via email



