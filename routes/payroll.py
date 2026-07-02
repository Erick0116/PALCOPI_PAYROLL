from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import supabase
from utils.payroll import calculate_employee_pay
from datetime import date

payroll_bp = Blueprint("payroll", __name__)

@payroll_bp.route('/payroll', methods=['GET'], endpoint='payroll')
def payroll():
    # Fetch employees and attendance
    employees = supabase.table("employees").select("*").execute().data
    attendance_records = supabase.table("attendance") \
        .select("*") \
        .eq("verify", False) \
        .execute().data

    # ✅ Fetch incentives with status "hold"
    incentives = supabase.table("incentive").select("*").eq("status", "hold").execute().data
    incentive_map = {}
    for i in incentives:
        incentive_map[i["name"]] = incentive_map.get(i["name"], 0) + float(i["amount"])

    # Filters
    query = request.args.get("search", "")
    period = request.args.get("period", "15")
    deduction = request.args.get("deduction", None)

    if query:
        employees = [e for e in employees if query.lower() in e["name"].lower()]

    payroll_data = []
    for emp in employees:
        emp_attendance = [r for r in attendance_records if r["name"] == emp["name"]]
        if emp_attendance:
            data = calculate_employee_pay(emp, emp_attendance, period, deduction)

            # Add incentives (only "hold")
            incentive_amount = incentive_map.get(emp["name"], 0)
            data["incentive"] = incentive_amount
            data["net_pay"] = data["net_pay"] + incentive_amount

            data["verify"] = False
            payroll_data.append(data)

    return render_template(
        "payroll.html",
        payroll=payroll_data,
        search=query,
        period=period,
        deduction=deduction
    )


@payroll_bp.route("/load_incentives", methods=["GET"])
def load_incentives():
    employees = supabase.table("employees").select("*").execute().data
    attendance = supabase.table("attendance").select("*").execute().data

    # ✅ Fetch incentives with status "hold"
    incentives = supabase.table("incentive").select("*").eq("status", "hold").execute().data
    incentive_map = {}
    for i in incentives:
        incentive_map[i["name"]] = incentive_map.get(i["name"], 0) + float(i["amount"])

    payroll_data = []
    for emp in employees:
        if not emp.get("verify", False):
            emp_attendance = [rec for rec in attendance if rec.get("name") == emp["name"]]

            result = calculate_employee_pay(emp, emp_attendance, week_number=1)

            incentive_amount = incentive_map.get(emp["name"], 0)
            result["incentive"] = incentive_amount
            result["net_pay"] = result["net_pay"] + incentive_amount

            payroll_data.append(result)

    return render_template("payroll.html", payroll=payroll_data, deduction=None, period="current")


@payroll_bp.route('/save_payroll', methods=['POST'], endpoint='save_payroll')
def save_payroll():
    period = request.form.get("period", "weekly")

    employees = supabase.table("employees").select("*").execute().data
    attendance_records = supabase.table("attendance") \
        .select("*") \
        .eq("verify", False) \
        .execute().data

    # ✅ Fetch incentives with status "hold"
    incentives = supabase.table("incentive").select("*").eq("status", "hold").execute().data
    incentive_map = {}
    for i in incentives:
        incentive_map[i["name"]] = incentive_map.get(i["name"], 0) + float(i["amount"])

    payroll_date = date.today().strftime("%Y-%m-%d")
    already_deducted = []

    for emp in employees:
        emp_attendance = [r for r in attendance_records if r["name"] == emp["name"]]
        payroll_data = calculate_employee_pay(emp, emp_attendance, period)

        # Add incentives (only "hold")
        incentive_amount = incentive_map.get(emp["name"], 0)
        payroll_data["incentive"] = incentive_amount
        payroll_data["net_pay"] = payroll_data["net_pay"] + incentive_amount

        # Check if employee already has deduction for this payroll_date
        existing = supabase.table("payroll") \
            .select("id, name, sss, pagibig, philhealth") \
            .eq("name", emp["name"]) \
            .eq("payroll_date", payroll_date) \
            .execute().data

        if existing and (
            existing[0]["sss"] > 0 or
            existing[0]["pagibig"] > 0 or
            existing[0]["philhealth"] > 0
        ):
            already_deducted.append(emp["name"])
            continue

        # Insert payroll record including incentive
        supabase.table("payroll").insert({
            "name": emp["name"],
            "salary": payroll_data["salary"],
            "sss": payroll_data["sss"],
            "pagibig": payroll_data["pagibig"],
            "philhealth": payroll_data["philhealth"],
            "payroll_date": payroll_date,
            "netpay": payroll_data["net_pay"],
            "total_hours": payroll_data["total_hours"],
            "incentive": payroll_data.get("incentive", 0)
        }).execute()

        # Mark attendance as verified
        for record in emp_attendance:
            supabase.table("attendance") \
                .update({"verify": True}) \
                .eq("id", record["id"]) \
                .execute()

    if already_deducted:
        flash(f"⚠️ These employees already have deductions for {payroll_date}: {', '.join(already_deducted)}", "warning")
    else:
        flash("Payroll records saved successfully!", "success")

    return redirect(url_for('payroll'))
