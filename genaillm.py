from dotenv import load_dotenv
from google.genai import Client
from google.genai.errors import ServerError
from schemas import ItemRow, DataCheck
from user_input_exception import UserInputError
import os

load_dotenv()

genai_api_key = os.environ["GENAI_API_KEY"]
EXIT_SERVER_ERROR = 5

#Gemini prompts for validating data and for extracting/formatting data
VALIDADTOR_PROMPT_TEMPLATE = f'''You are a data validator, designed to ensure that data complies with a specific schema, and returning certain boolean values based on the data presented. Your task is to parse the data, identify if there are or if there are not any missing elements based on the provided schema, and return a certain values depending on the state of the data. The output should be in a JSON object format.

Here is the strict JSON schema you are to follow:

{{
“customer_name”: boolean,
“description”: boolean,
“units”: boolean,
“price_per_unit”: boolean
}}

Here are examples of how to format your output:

---

Input:
"For Mrs. Thatcher, invoice 10 premium rugs, $500 apiece, dated July 1st 2025."

Output:
{{
  "customer_name": true,
  "description": true,
  "units": true,
  "price_per_unit": true
}}

---

Input:
"We received an order from Sarah Lee for 5 boxes of envelopes. This is for the office supply cabinet."

Output:
{{
  "customer_name": true,
  "description": true,
  "units": true,
  "price_per_unit": false
}}

---

Input:
"Ordered 12 cases of bottled water for the event. Each case cost R6.50."

Output:
{{
  "customer_name": false,
  "description": true,
  "units": true,
  "price_per_unit": true
}}

---

Input:
"Just a reorder, same as last time, for about 20 items."

Output:
{{
  "customer_name": false,
  "description": false,
  "units": true,
  "price_per_unit": false
}}

---

Input:
"Maria Gonzalez placed a rush order for 7 crates of bottled ink at R149.99 per crate. It’s for their studio renovation project."

Output:
{{
  "customer_name": true,
  "description": true,
  "units": true,
  "price_per_unit": true
}}

---

Input:
"Can you bill Sarah Lin for 1 set of kitchen tiles at $750 and 3 bags of grout at $20 each?"

Output:
{{
  "customer_name": true,
  "description": true,
  "units": true,
  "price_per_unit": true
}}

Now, process the following input:

'''

INVOICE_PROMPT_TEMPLATE = f'''You are a data extraction assistant designed to validate and extract invoice information from free-form user input. Your task is to parse the input and convert it into a JSON object that matches a strict schema.

The output must follow this JSON schema:

{{
  "customer_name": string,
  "date": string | null,
  "vat_inclusive": boolean = True,
  "vat_exclusive": boolean = False,
  "must_show_vat": boolean = True,
  "vat_perc" : integer = 15,
  "description": list of strings,
  "units": list of integers,
  "price_per_unit": list of floats,
  "price_of_item": list of floats,
  "deposit": float = 0.00
  "discount": float = 0.00,
}}

Here are examples of how to format your output:

---

Input:
"I need an invoice for John Smith for 3 wooden tables at $100 each and 2 chairs at $50 each. Date is 30 June 2025."

Output:
{{
  "customer_name": "John Smith",
  "date": "2025-06-30",
  "vat_inclusive": True,
  "must_show_vat": True,
  "vat_perc" : 15,
  "description": ["Wooden Tables", "Chairs"],
  "units": [3, 2],
  "price_per_unit": [100.00, 50.00],
  "price_of_item": [300.00, 100.00],
  "deposit": 0.00,
  "discount": 0.00,
}}

---

Input:
"Harry needs five hours of graphic design work at 150 per hour, and two hours for some editing at the same rate. July 1st 2025. Do not show VAT."

Output:
{{
  "customer_name": "Harry",
  "date": "2025-07-01",
  "vat_inclusive": True,
  "must_show_vat": False,
  "vat_perc" : 15,
  "description": ["Graphic Design Work", "Editing"],
  "units": [5, 2],
  "price_per_unit": [150.00, 150.00],
  "price_of_item": [750, 300],
  "deposit": 0.00,
  "discount": 0.00,
}}

---

Input:
"Bill Martin for web design: 7 hours @ $35/hour. Add VAT."

Output:
{{
  "customer_name": "Martin",
  "date": None,
  "vat_inclusive": False,
  "must_show_vat": True,
  "vat_perc" : 15,
  "description": ["Web Design",],
  "units": [7],
  "price_per_unit": [35.00],
  "price_of_item": [245.00],
  "deposit": 0.00,
  "discount": 0.00,
}}

---

Input:
"Please quote for the following order:

1 x Reception Desk to measure 2,2m L in Supawood and Meranti as per customer’s reference image, with a gloss finish, @ $11500
1 x  Kitchen cupboards in Supawood and Melamine as per customer’s reference image and spec’s, measuring at 2,6m, @ $12500

This is for Rachel Adams. The prices are not VAT inclusive."

Output:
{{
  "customer_name": "Rachel Adams",
  "date": None,
  "vat_inclusive": False,
  "must_show_vat": True,
  "vat_perc" : 15,
  "description": ["1 x Reception Desk to measure 2,2m L in Supawood and Meranti as per customer’s reference image, with a gloss finish", "1 x  Kitchen cupboards in Supawood and Melamine as per customer’s reference image and spec’s, measuring at 2,6m"],
  "units": [1, 1],
  "price_per_unit": [11500.00, 12500.00],
  "price_of_item": [11500.00, 12500.00],
  "deposit": 0.00,
  "discount": 0.00,
}}

---

Input:
"Hey there. I need an invoice for a really big order. It is for a client named 'SupaBoxes'. Please put today's date. Prices are VAT exclusive. And VAT is 16%. They paid Here the details below:

Pyjama lounge wooden wall panels behind TV, measuring 1,9m L x 2,05m H. - R4800
Bedroom 4 wooden wall panels, measuring at 1,2m x 2,2m. - R4050
Bedroom 5 Half-moon mirror, measuring at 1m L x 800mm W. - R1900
Main Lounge Sectional Couch in Loomcraft fabric colour 19, measuring at 5,5m x 2,4m. - R26000
Wall molding. 15m @ R400/m, with R100 installation fee per meter."

They paid a R22125 deposit.

Output:
{{
  "customer_name": "SupaBoxes",
  "date": None,
  "vat_inclusive": False,
  "must_show_vat": True,
  "vat_perc" : 16,
  "description": ["Pyjama lounge wooden wall panels behind TV, measuring 1,9m L x 2,05m H", "Bedroom 4 wooden wall panels, measuring at 1,2m x 2,2m", "Bedroom 5 Half-moon mirror, measuring at 1m L x 800mm W", "Main Lounge Sectional Couch in Loomcraft fabric colour 19, measruing at 5,5m x 2,4m", "Wall molding. 15m @ R400/m, with R100 installation fee per meter."],
  "units": [1, 1, 1, 1, 15],
  "price_per_unit": [4800.00, 4050.00, 1900, 26000, 500],
  "price_of_item": [4800.00, 4050.00, 1900.00, 26000,00, 7500.00],
  "deposit": 22125.00,
  "discount": 0.00,
}}

---

Input:
"Charge Jane: 4x private math tutoring @ $90. No VAT. Oct, 15 25. 5% discount."

Output:
{{
  "customer_name": "Jane",
  "date": 2025-10-15,
  "vat_inclusive": True,
  "must_show_vat": False,
  "vat_perc" : 15,
  "description": ["Private Math Tutoring"],
  "units": [4],
  "price_per_unit": [90.00],
  "price_of_item": [360.00],
  "deposit": 0.00,
  "discount": 5.00,
}}

Now, process the following input:

'''
class InvoiceLLM:
    def __init__(self):
        self.model = "gemini-2.0-flash"
        self.client = Client(api_key=genai_api_key)

    #Uses LLM to validate data and return error object if erroneous
    def validate_data(self, data):
        missing_elements = []

        data_input = self.client.models.generate_content(
            model=self.model,
            contents=VALIDADTOR_PROMPT_TEMPLATE + data,
            config={
                "response_mime_type": "application/json",
                "response_schema": DataCheck,
            }
        )

        data_input = data_input.parsed.model_dump()

        for (key, value) in data_input.items():
            if not value:
                missing_elements.append(key)

        if missing_elements:
            return UserInputError(user_input=data, misc_elements=missing_elements)
        else:
            return data

    def arrange_data(self, user_input):
        try:
            valid_input = self.validate_data(data=user_input)
        except ServerError:
            return ServerError

        if isinstance(valid_input, UserInputError):
            return valid_input
        try:
            data = self.client.models.generate_content(
                model=self.model,
                contents=INVOICE_PROMPT_TEMPLATE + valid_input,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ItemRow,
                }
            )
        except ServerError:
            return ServerError

        response = data.parsed
        return response.model_dump()
