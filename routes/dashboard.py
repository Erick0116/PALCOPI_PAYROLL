from flask import Blueprint, render_template
from config import supabase
from datetime import date, datetime

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route('/', endpoint='dashboard')
def dashboard():
    # Fetch all employees
    employees_response = supabase.table("employees").select("id").execute()
    employees = employees_response.data
    total_employees = len(employees)

    # Fetch all attendance records
    attendance_response = supabase.table("attendance").select("*").execute()
    records = attendance_response.data

    # Today's records
    today_str = date.today().isoformat()
    today_records = [r for r in records if r["date"] == today_str]

    # Cutoff time for "on time"
    cutoff = datetime.strptime("09:00", "%H:%M").time()

    # Count on-time vs late today
    on_time_today = sum(
        1 for r in today_records
        if r["time_in"] and datetime.strptime(r["time_in"], "%H:%M").time() <= cutoff
    )
    late_today = len(today_records) - on_time_today

    # On-time percentage
    on_time_percentage = (on_time_today / total_employees * 100) if total_employees else 0

    # Monthly report
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    ontime_counts = [0]*12
    late_counts = [0]*12

    for r in records:
        record_date = datetime.strptime(r["date"], "%Y-%m-%d")
        month_index = record_date.month - 1
        if r["time_in"]:
            time_in = datetime.strptime(r["time_in"], "%H:%M").time()
            if time_in <= cutoff:
                ontime_counts[month_index] += 1
            else:
                late_counts[month_index] += 1

    monthly_report = {
        "months": months,
        "ontime": ontime_counts,
        "late": late_counts
    }

    metrics = {
        "total_employees": total_employees,
        "on_time_percentage": round(on_time_percentage, 2),
        "on_time_today": on_time_today,
        "late_today": late_today
    }

    return render_template("dashboard.html", metrics=metrics, report=monthly_report)
