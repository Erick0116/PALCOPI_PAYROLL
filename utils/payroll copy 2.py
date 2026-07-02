from datetime import date, datetime, timedelta
from utils.settings import load_settings

def calculate_employee_pay(emp, attendance_records, week_number, deduction=None):
    settings = load_settings()
    overtime_rate = settings.get("overtime_rate", 1.5)
    overtime_threshold = settings.get("overtime_threshold", 8)

    # Late deduction settings from Supabase
    late_grace_minutes = int(settings.get("late_grace_minutes", 5))       # grace period
    late_minor_minutes = int(settings.get("late_minor_minutes", 10))      # minor lateness threshold
    late_major_minutes = int(settings.get("late_major_minutes", 30))      # major lateness threshold
    late_deduction_hours = float(settings.get("late_deduction_hours", 1)) # hours deducted for minor lateness
    late_major_deduction_hours = float(settings.get("late_major_deduction_hours", 2)) # hours deducted for >30 mins

    total_hours = 0
    overtime_hours = 0
    late_count = 0
    late_minutes_total = 0        # NEW: track total minutes late
    late_deduction_total = 0      # total deduction hours applied

    for record in attendance_records:
        if record.get("time_in") and record.get("time_out"):
            try:
                time_in = datetime.strptime(record["time_in"], "%H:%M").time()
                time_out = datetime.strptime(record["time_out"], "%H:%M").time()
                dt_in = datetime.combine(date.today(), time_in)
                dt_out = datetime.combine(date.today(), time_out)

                if time_out < time_in:  # overnight shift
                    dt_out += timedelta(days=1)

                worked_hours = (dt_out - dt_in).total_seconds() / 3600

                if 0 < worked_hours <= 24:
                    if worked_hours > overtime_threshold:
                        total_hours += overtime_threshold
                        overtime_hours += worked_hours - overtime_threshold
                    else:
                        total_hours += worked_hours

                # Lateness calculation
                scheduled_start = datetime.strptime("09:00", "%H:%M").time()
                if time_in > scheduled_start:
                    minutes_late = (datetime.combine(date.today(), time_in) -
                                    datetime.combine(date.today(), scheduled_start)).total_seconds() / 60

                    if minutes_late > late_grace_minutes:
                        late_count += 1
                        late_minutes_total += minutes_late  # accumulate minutes late
                        if late_minor_minutes <= minutes_late <= late_major_minutes:
                            late_deduction_total += late_deduction_hours
                        elif minutes_late > late_major_minutes:
                            late_deduction_total += late_major_deduction_hours

            except Exception:
                pass

    hour_rate = float(emp.get("hour_rate", 0))
    regular_pay = total_hours * hour_rate
    overtime_pay = overtime_hours * (hour_rate * overtime_rate)
    salary = regular_pay + overtime_pay

    # Deduct lateness penalty (convert hours to pay)
    salary -= late_deduction_total * hour_rate

    # Deduction values from Supabase
    sss_weekly = float(settings.get("sss_weekly", 0))
    philhealth_weekly = float(settings.get("philhealth_weekly", 0))
    pagibig_weekly = float(settings.get("pagibig_weekly", 0))

    sss = pagibig = philhealth = 0

    if deduction == "sss" and str(emp.get("sss")).lower() in ["true", "1"]:
        sss = sss_weekly
    elif deduction == "philhealth" and str(emp.get("philhealth")).lower() in ["true", "1"]:
        philhealth = philhealth_weekly
    elif deduction == "pagibig" and str(emp.get("pagibig")).lower() in ["true", "1"]:
        pagibig = pagibig_weekly
    else:
        if week_number == 1 and str(emp.get("sss")).lower() in ["true", "1"]:
            sss = sss_weekly
        elif week_number == 2 and str(emp.get("philhealth")).lower() in ["true", "1"]:
            philhealth = philhealth_weekly
        elif week_number == 3 and str(emp.get("pagibig")).lower() in ["true", "1"]:
            pagibig = pagibig_weekly

    net_pay = salary - (sss + pagibig + philhealth)

    return {
        "id": emp["id"],
        "name": emp["name"],
        "total_hours": round(total_hours, 2),
        "overtime_hours": round(overtime_hours, 2),
        "late_count": late_count,
        "late_minutes": round(late_minutes_total, 2),          # NEW FIELD
        "late_deduction_hours": round(late_deduction_total, 2),
        "regular_pay": round(regular_pay, 2),
        "overtime_pay": round(overtime_pay, 2),
        "salary": round(salary, 2),
        "sss": round(sss, 2),
        "pagibig": round(pagibig, 2),
        "philhealth": round(philhealth, 2),
        "net_pay": round(net_pay, 2),
        "verify": False
    }
