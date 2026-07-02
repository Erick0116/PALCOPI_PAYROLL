from config import app
from routes.dashboard import dashboard_bp
from routes.attendance import attendance_bp
from routes.employees import employees_bp
from routes.payroll import payroll_bp
from routes.payslip import payslip_bp
from routes.deduction import deduction_bp   # ✅ add this
from routes.incentive import incentive_bp
from routes.cash_advance import cash_advance_bp

# Register blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(payroll_bp)
app.register_blueprint(payslip_bp)
app.register_blueprint(deduction_bp)  
app.register_blueprint(incentive_bp)   
app.register_blueprint(cash_advance_bp)

if __name__ == '__main__':
    app.run(debug=True)
