from pydantic import BaseModel

class DataCheck(BaseModel):
    customer_name: bool
    description: bool
    units: bool
    price_per_unit: bool

class ItemRow(BaseModel):
    customer_name : str
    date : str | None = None
    vat_inclusive : bool = True
    must_show_vat : bool = True
    vat_perc : int = 15
    description : list[str]
    units : list[int]
    price_per_unit : list[float]
    price_of_item : list[float]