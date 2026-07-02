from flask import Blueprint, request, render_template, redirect, url_for
from utils.attendance_utils import (
    get_all_attendance, filter_attendance,
    add_attendance, update_attendance,
    delete_attendance
)

attendance_bp = Blueprint("attendance", __name__)

# Main listing route
@attendance_bp.route('/attendance', methods=['GET'], endpoint='attendance')
def attendance():
    records = get_all_attendance()
    query = request.args.get("search", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    records = filter_attendance(records, query, date_from, date_to)
    return render_template("attendance.html", records=records,
                           search=query, date_from=date_from, date_to=date_to)

# New record route
@attendance_bp.route('/attendance/new', methods=['POST'], endpoint='new_attendance')
def new_attendance():
    add_attendance(
        request.form['id'],
        request.form['name'],
        request.form['date'],
        request.form['time_in'],
        request.form['time_out']
    )
    return redirect(url_for('attendance'))

# Edit record route (only POST, since modal handles the form)
@attendance_bp.route('/attendance/edit/<int:emp_id>', methods=['POST'], endpoint='edit_attendance')
def edit_attendance(emp_id):
    update_attendance(
        emp_id,
        request.form['name'],
        request.form['date'],
        request.form['time_in'],
        request.form['time_out']
    )
    return redirect('/attendance')

# Delete record route
@attendance_bp.route('/attendance/delete/<int:emp_id>', methods=['POST'], endpoint='delete_attendance')
def delete_attendance_route(emp_id):
    delete_attendance(emp_id)
    return redirect(url_for('attendance'))
