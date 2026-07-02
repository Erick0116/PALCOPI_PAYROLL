from flask import Blueprint, request, render_template, redirect, url_for
from config import supabase

employees_bp = Blueprint("employees", __name__)

@employees_bp.route('/employees', methods=['GET'], endpoint='employees')
def employees():
    response = supabase.table("employees").select("*").execute()
    records = response.data

    query = request.args.get("search", "")
    if query:
        records = [r for r in records if query.lower() in r["name"].lower()]

    return render_template("employees.html", records=records, search=query)

@employees_bp.route('/employees/new', methods=['POST'])
def new_employee():
    emp_id = request.form['id']
    name = request.form['name']
    birthdate = request.form['birthdate']
    status = request.form['employment_status']
    position = request.form['position']
    hour_rate = request.form['hour_rate']

    sss = 'SSS' in request.form.getlist('benefits')
    pagibig = 'Pagibig' in request.form.getlist('benefits')
    philhealth = 'Philhealth' in request.form.getlist('benefits')

    supabase.table("employees").insert({
        "id": emp_id,
        "name": name,
        "birthdate": birthdate,
        "employment_status": status,
        "position": position,
        "hour_rate": hour_rate,
        "sss": sss,
        "pagibig": pagibig,
        "philhealth": philhealth
    }).execute()

    return redirect(url_for('employees.employees'))
