from config import supabase

def get_all_attendance():
    """Fetch all attendance records from Supabase."""
    response = supabase.table("attendance").select("*").execute()
    return response.data

def filter_attendance(records, search="", date_from="", date_to=""):
    """Filter attendance records by search term and date range."""
    if search:
        records = [r for r in records if search.lower() in r["name"].lower()]
    if date_from and date_to:
        records = [r for r in records if date_from <= r["date"] <= date_to]
    return records

def add_attendance(emp_id, name, date, time_in, time_out):
    """Insert a new attendance record."""
    supabase.table("attendance").insert({
        "id": emp_id,
        "name": name,
        "date": date,
        "time_in": time_in,
        "time_out": time_out
    }).execute()

def update_attendance(emp_id, name, date, time_in, time_out):
    """Update an existing attendance record."""
    supabase.table("attendance").update({
        "name": name,
        "date": date,
        "time_in": time_in,
        "time_out": time_out
    }).eq("id", emp_id).execute()

def delete_attendance(emp_id):
    """Delete an attendance record."""
    supabase.table("attendance").delete().eq("id", emp_id).execute()

def get_attendance_by_id(emp_id):
    """Fetch a single attendance record by ID."""
    record = supabase.table("attendance").select("*").eq("id", emp_id).execute().data
    return record[0] if record else None
