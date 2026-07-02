from flask import Blueprint, request, render_template, redirect, url_for
from config import supabase
from datetime import date

deduction_bp = Blueprint("deduction", __name__)

@deduction_bp.route('/deduction', methods=['GET'], endpoint='deduction')
def deduction():
    # Load employees so you can show them in the deduction table
    response = supabase.table("employees").select("*").execute()
    records = response.data
    return render_template("deduction.html", records=records)

@deduction_bp.route('/deduction/add', methods=['POST'], endpoint='add_deduction')
def add_deduction():
    emp_id = int(request.form['emp_id'])
    name = request.form['name']
    deduction_type = request.form['deduction_type']
    deduction_amount = float(request.form.get('deduction_amount', 0))
    deduction_details = request.form.get('deduction_details', "")

    # Handle charge date
    charge_date_option = request.form.get('charge_date_option')
    charge_date_custom = request.form.get('charge_date_custom')
    if charge_date_option == "custom" and charge_date_custom:
        date_deduct = charge_date_custom
    else:
        today = date.today()
        day = int(charge_date_option)
        date_deduct = today.replace(day=day).isoformat()

    # Fetch existing record for this employee
    existing = supabase.table("deduction").select("*").eq("id", emp_id).execute().data

    if existing:
        record = existing[0]  # current row
        # Update only the relevant field
        if deduction_type == "SSS":
            record["sss"] = deduction_amount
        elif deduction_type == "Pagibig":
            record["pagibig"] = deduction_amount
        elif deduction_type == "Philhealth":
            record["philhealth"] = deduction_amount
        elif deduction_type == "Cash Advance":
            record["cash_advance"] = deduction_amount
        elif deduction_type == "Charges":
            record["charges"] = deduction_amount
            record["charges_details"] = deduction_details
        elif deduction_type == "Others":
            record["other_charges"] = deduction_amount
            record["other_details"] = deduction_details

        # Always update date_deduct and name
        record["date_deduct"] = date_deduct
        record["name"] = name

        supabase.table("deduction").update(record).eq("id", emp_id).execute()

    else:
        # Insert new record with defaults
        record = {
            "id": emp_id,
            "name": name,
            "sss": 0,
            "pagibig": 0,
            "philhealth": 0,
            "cash_advance": 0,
            "charges": 0,
            "charges_details": "",
            "other_charges": 0,
            "other_details": "",
            "date_deduct": date_deduct,
            "deducted": False
        }

        if deduction_type == "SSS":
            record["sss"] = deduction_amount
        elif deduction_type == "Pagibig":
            record["pagibig"] = deduction_amount
        elif deduction_type == "Philhealth":
            record["philhealth"] = deduction_amount
        elif deduction_type == "Cash Advance":
            record["cash_advance"] = deduction_amount
        elif deduction_type == "Charges":
            record["charges"] = deduction_amount
            record["charges_details"] = deduction_details
        elif deduction_type == "Others":
            record["other_charges"] = deduction_amount
            record["other_details"] = deduction_details

        supabase.table("deduction").insert(record).execute()

    return redirect(url_for('deduction'))
