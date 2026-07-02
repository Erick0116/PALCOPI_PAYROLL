from flask import Blueprint, render_template
from config import supabase
from utils.tax import compute_income_tax

payslip_bp = Blueprint("payslip", __name__)

@payslip_bp.route('/payslip/<int:emp_id>')
def payslip(emp_id):
    emp = supabase.table("employees").select("*").eq("id", emp_id).execute().data[0]

    salary = float(emp.get("hour_rate", 0)) * 160

    sss = salary * 0.045 if emp.get("sss") else 0
    pagibig = salary * 0.02 if emp.get("pagibig") else 0
    philhealth = salary * 0.0275 if emp.get("philhealth") else 0

    taxable_income_monthly = salary - (sss + pagibig + philhealth)
    annual_taxable_income = taxable_income_monthly * 12
    annual_tax = compute_income_tax(annual_taxable_income)
    income_tax = annual_tax / 12

    net_pay = salary - (sss + pagibig + philhealth + income_tax)

    return render_template("payslip.html", emp=emp, salary=salary,
                           sss=sss, pagibig=pagibig, philhealth=philhealth,
                           income_tax=income_tax, net_pay=net_pay)
