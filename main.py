from genaillm import InvoiceLLM
from google_suite.drive import Drive
from google_suite.docs import Docs, CURRENCY
from user_input_exception import UserInputError
from google.genai.errors import ServerError
from datetime import datetime
import streamlit as st

st.title("MCF Invoice Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_invoice_data" not in st.session_state:
    st.session_state["user_invoice_data"] = {}

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Creates Gemini LMM instance for NLP
g_llm = InvoiceLLM()

#Defines a function for calculating totals for customer invoice (Subtotal, VAT, etc.)
def calculate_totals(data):
    vat_perc = (data["vat_perc"] / 100) + 1
    subtotal = 0

    for item in range(len(data["description"])):
        try:
            subtotal += data["price_of_item"][item]
        except TypeError:
            pass

    if data["discount"]:
        subtotal -= subtotal * (data["discount"] / 100)

    vat_amount = subtotal - (subtotal / vat_perc)
    nett_amount = subtotal / vat_perc
    if data["deposit"]:
        total_due = subtotal - data["deposit"]
    else:
        total_due = subtotal

    totals = {
        "subtotal": f"{subtotal:.2f}",
        "vat": f"{vat_amount:.2f}",
        "nett": f"{nett_amount:.2f}",
        "total_due": f"{total_due:.2f}",
    }

    return totals

if "messages" not in st.session_state:
    st.session_state.messages = []

#Asks the user what they want to put in their invoice


#Processes and validates the user input via LLM instance


if user_input := st.chat_input(placeholder="Type here..."):
    try:
        st.session_state["user_invoice_data"] = g_llm.arrange_data(user_input)
    except ServerError:
        err_message = "There seems to be a server error. Try again in a bit."
        with st.chat_message("ai"):
            st.write(err_message)
            st.session_state.messages.append({"role": "ai", "content": err_message})
    except TypeError:
        data = g_llm.arrange_data(user_input)

        if isinstance(data, ServerError):
            err_message = "There seems to be a server error. Try again in a bit."
            with st.chat_message("ai"):
                st.write(err_message)
                st.session_state.messages.append({"role": "ai", "content": err_message})

        elif isinstance(data, UserInputError):
            with st.chat_message("ai"):
                st.write(data)
    else:

        st.session_state.messages.append({"role": "user", "content": user_input})
        #Adds today's date if user specified so or if they did not specify a date entirely
        data = st.session_state["user_invoice_data"]
        if st.session_state["user_invoice_data"]["date"] is None:
            data["date"] = datetime.today().strftime("%Y-%m-%d")

        #Make a copy of the invoice template and create unique invoice number
        gdr = Drive(data=data)
        invoice_num = gdr.create_invoice_num()

        #Acquire the unique documentId for the Google Docs API
        customer_invoice_data = gdr.get_template_copy()
        customer_invoice_id = customer_invoice_data["id"]

        #Adds VAT to pricing if user indicated that prices are not VAT inclusive
        if not data["vat_inclusive"]:
            vat_decimal = data["vat_perc"] / 100
            data["price_per_unit"] = [num + (num * vat_decimal) for num in data["price_per_unit"]]
            data["price_of_item"] = [num + (num * vat_decimal) for num in data["price_of_item"]]

        #Adds row to indicate the deposit if user included it in prompt
        if data["deposit"]:
            data["description"].append(f"({CURRENCY}{data["deposit"]:.2f} Deposit)")
            data["units"].append(" ")
            data["price_per_unit"].append(" ")
            data["price_of_item"].append(f"({CURRENCY}{data["deposit"]:.2f})")

        #Adds row to indicate the discount if user included it in prompt
        if data["discount"]:
            data["description"].append(f"({data["discount"]:.2f}% Discount)")
            data["units"].append(" ")
            data["price_per_unit"].append(" ")
            data["price_of_item"].append(f"({data["discount"]:.2f}%)")

        #Creates Google Docs instance and inserts & populates rows
        gdc = Docs(docId=customer_invoice_id, data=data, invnum=invoice_num)
        gdc.insert_rows()
        gdc.populate_rows()

        # Adds the totals to the customer invoice
        invoice_totals = calculate_totals(data=data)
        gdc.include_totals(totals_set=invoice_totals)

        with st.chat_message("ai"):
            success_message = "✅ Your invoice has been generated successfully! Check your Google Docs." #✅ Your invoice has been generated successfully! Check your Google Docs.
            st.write(success_message)
            st.session_state.messages.append({"role": "ai", "content": success_message})

