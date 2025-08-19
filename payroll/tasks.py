from celery import shared_task
from .services.salary_processor import EmployeeSalaryProcessor, AllOrgPayrollProcessor
from payroll.models import PayrollOrg
from datetime import date


@shared_task
def process_all_orgs_salary_task():
    today = date.today()

    # Financial year format: "2024-2025"
    fy_start = today.year if today.month >= 4 else today.year - 1
    financial_year = f"{fy_start}-{fy_start + 1}"
    month = today.month

    print(f"[INFO] Running salary processing for all orgs: FY={financial_year}, Month={month}")
    AllOrgPayrollProcessor(financial_year, month).run()
    print("[INFO] Payroll processing completed.")


