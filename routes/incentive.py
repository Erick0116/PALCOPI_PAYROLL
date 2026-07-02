from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import supabase
import datetime

incentive_bp = Blueprint('incentive', __name__, url_prefix='/incentive')

@incentive_bp.route('/')
def incentive():
    employees = supabase.table("employees").select("name, employment_status, position").execute().data
    return render_template('incentive.html', employees=employees)

@incentive_bp.route('/add', methods=['POST'])
def add_incentive():
    name = request.form['name']
    incentive_type = request.form['incentive_type']
    description = request.form['description']
    amount = request.form['amount']
    date = datetime.date.today().isoformat()

    # ✅ Add status field
    status = "hold"  # or request.form['status'] if you want a dropdown

    supabase.table("incentive").insert({
        "name": name,
        "incentive_type": incentive_type,
        "description": description,
        "amount": amount,
        "date": date,
        "status": status
    }).execute()

    flash("Incentive added successfully!", "success")
    return redirect(url_for('incentive.incentive'))
