from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import supabase
import datetime

cash_advance_bp = Blueprint('cash_advance', __name__, url_prefix='/cash_advance')

@cash_advance_bp.route('/')
def cash_advance():
    employees = supabase.table("employees").select("name, employment_status, position").execute().data
    current_date = datetime.date.today().isoformat()
    return render_template('cash_advance.html', employees=employees, current_date=current_date)

@cash_advance_bp.route('/add', methods=['POST'])
def add_cash_advance():
    name = request.form['name']
    type_ = request.form['type']
    amount = request.form['amount']
    date = request.form['date']

    supabase.table("cash_advance").insert({
        "name": name,
        "type": type_,
        "amount": amount,
        "date": date
    }).execute()

    flash("Cash advance added successfully!", "success")
    return redirect(url_for('cash_advance.cash_advance'))
