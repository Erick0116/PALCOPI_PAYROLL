from config import supabase

def compute_income_tax(annual_taxable_income):
    response = supabase.table("tax_brackets").select("*").execute()
    brackets = response.data
    brackets.sort(key=lambda b: b["min_income"])

    for b in brackets:
        max_income = b["max_income"]
        if max_income is None or annual_taxable_income <= max_income:
            base_tax = float(b["base_tax"])
            rate = float(b["rate"])
            return base_tax + (annual_taxable_income - b["min_income"]) * rate
    return 0
