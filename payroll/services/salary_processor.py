# payroll/services/employee_salary_processor.py
from datetime import date
import traceback
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status

from payroll.models import (
    PayrollWorkflow, EmployeeSalaryDetails, EmployeeExit, EmployeeAttendance,
    Earnings, BonusIncentive, EmployeeSalaryHistory, PayrollOrg
)
from payroll.serializers import EmployeeSalaryHistorySerializer
from payroll.helpers import is_valid_number, calculate_component_amounts, calculate_tds
from botocore.exceptions import BotoCoreError, ClientError
import boto3
from datetime import date
from django.db.models import Sum
import traceback
from Tara.settings.default import *


class EmployeeSalaryProcessor:
    def __init__(self, payroll_org, financial_year, month):
        self.today = date.today()
        self.payroll_org = payroll_org
        self.financial_year = financial_year
        self.month = month
        self.year = int(financial_year.split('-')[0]) if month >= 4 else int(financial_year.split('-')[0]) + 1

    def process(self):
        if not self.financial_year or not self.month:
            return

        if self.today.day < 26 and self.month == self.today.month:
            return

        payroll_workflow = PayrollWorkflow.objects.filter(
            payroll=self.payroll_org,
            month=self.month,
            financial_year=self.financial_year
        ).first()

        if not payroll_workflow or payroll_workflow.lock_payroll:
            return

        salary_records = EmployeeSalaryDetails.objects.filter(
            employee__payroll=self.payroll_org
        )
        if not salary_records.exists():
            return

        FINANCIAL_MONTH_MAP = {1: 10, 2: 11, 3: 12, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9}
        current_month = FINANCIAL_MONTH_MAP.get(self.month, 1)

        for salary_record in salary_records:
            employee = salary_record.employee

            # Skip exited employees
            exit_obj = EmployeeExit.objects.filter(employee=employee).last()
            if exit_obj:
                if (exit_obj.exit_year < self.year) or (
                    exit_obj.exit_year == self.year and exit_obj.exit_month < self.month
                ):
                    continue

            try:
                attendance = EmployeeAttendance.objects.get(
                    employee=employee,
                    financial_year=self.financial_year,
                    month=self.month
                )
            except EmployeeAttendance.DoesNotExist:
                continue

            total_working_days = attendance.total_days_of_month - attendance.loss_of_pay
            gross_salary = salary_record.gross_salary.get("monthly", 0)
            per_day_salary = gross_salary / attendance.total_days_of_month
            earned_salary = per_day_salary * total_working_days
            lop_amount = per_day_salary * attendance.loss_of_pay

            # EPF
            epf_earnings = Earnings.objects.filter(
                payroll=self.payroll_org,
                includes_epf_contribution=True
            )

            component_amount_map = {
                item["component_name"].lower().replace(" ", "_"): item.get("monthly", 0)
                for item in salary_record.earnings
            }

            epf_eligible_total = 0
            for earning in epf_earnings:
                name = earning.component_name.lower().replace(" ", "_")
                value = component_amount_map.get(name, 0)
                epf_eligible_total += (value * total_working_days) / attendance.total_days_of_month

            epf_base = min(epf_eligible_total, 15000)
            pf = round(epf_base * 0.12, 2)

            # ESI
            esi = round(earned_salary * 0.0075, 2) if gross_salary <= 21000 else 0

            # PT default
            pt_amount = 0

            # Benefits total
            benefits_total = sum(
                b["monthly"] for b in (salary_record.benefits or []) if isinstance(b.get("monthly"), (int, float))
            )

            # Taxes
            taxes = sum(
                float(d["monthly"]) for d in salary_record.deductions
                if "Tax" in d.get("component_name", "") and is_valid_number(d.get("monthly"))
            )

            # Loan EMI
            advance_loan = getattr(employee, "employee_advance_loan", None)
            emi_deduction = 0
            if advance_loan:
                active_loan = advance_loan.filter(
                    start_month__lte=date(self.today.year, self.month, 1),
                    end_month__gte=date(self.today.year, self.month, 1)
                ).first()
                if active_loan:
                    emi_deduction = float(active_loan.emi_amount or 0)

            def prorate(value):
                return (value * total_working_days) / attendance.total_days_of_month if value else 0

            component_amounts = calculate_component_amounts(
                salary_record.earnings, total_working_days, attendance.total_days_of_month
            )

            epf_value = 0
            employee_deductions = 0
            other_deductions = 0
            pt_set = False
            other_deductions_breakdown = []

            for deduction in salary_record.deductions or []:
                name = deduction.get("component_name", "").lower().replace(" ", "_")
                value = deduction.get("monthly", 0)
                value = value if isinstance(value, (int, float)) else 0

                if name == "epf_employee_contribution" and employee.statutory_components.get("epf_enabled"):
                    full_month_basic = component_amounts['basic']
                    epf_contribution = 1800 if full_month_basic > 15000 else round(full_month_basic * 0.12, 2)
                    employee_deductions += epf_contribution
                    epf_value = epf_contribution

                elif name == "pt" and employee.statutory_components.get("professional_tax", False):
                    pt_amount = value
                    pt_set = True

                elif name == "tds":
                    employee_deductions += value

                elif all(k not in name for k in ["epf_employee_contribution", "esi_employee_contribution", "pt", "tds", "loan_emi"]):
                    prorated = prorate(value)
                    other_deductions += prorated
                    if prorated > 0:
                        other_deductions_breakdown.append({name: round(prorated, 2)})

            total_deductions = taxes + emi_deduction + employee_deductions + other_deductions + pt_amount + esi
            net_salary = earned_salary - total_deductions

            # Bonus
            total_bonus_amount = BonusIncentive.objects.filter(
                employee=employee,
                month=self.month,
                financial_year=self.financial_year
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            existing_record = EmployeeSalaryHistory.objects.filter(
                employee=employee,
                payroll=self.payroll_org,
                financial_year=self.financial_year,
            ).first()

            recalculate_tds = False
            if existing_record:
                recalculate_tds = (
                    existing_record.ctc != salary_record.annual_ctc or
                    total_bonus_amount > 0 or
                    (attendance.loss_of_pay > 0 and lop_amount > 0)
                )

            tds_ytd, annual_tds = 0, 0
            if existing_record and not recalculate_tds:
                monthly_fixed_tds = round(max(0, (existing_record.annual_tds - existing_record.tds_ytd)) / (13 - current_month))
                monthly_tds = monthly_fixed_tds
                tds_ytd = existing_record.tds_ytd + monthly_tds
                annual_tds = existing_record.annual_tds
            else:
                annual_gross = int(round(per_day_salary * attendance.total_days_of_month, 2)) * 12
                if total_bonus_amount:
                    annual_gross += total_bonus_amount
                if attendance.loss_of_pay > 0 and lop_amount > 0:
                    annual_gross -= lop_amount

                monthly_tds, annual_tds = calculate_tds(
                    regime_type=salary_record.tax_regime_opted,
                    annual_salary=annual_gross,
                    current_month=current_month,
                    epf_value=epf_value,
                    ept_value=pt_amount,
                    bonus_or_revisions=recalculate_tds
                )
                if existing_record:
                    monthly_tds = round(max(0, (annual_tds - existing_record.tds_ytd)) / (13 - current_month))
                    tds_ytd = existing_record.tds_ytd + monthly_tds
                else:
                    tds_ytd = monthly_tds

                monthly_fixed_tds = monthly_tds

            # Finalize
            total_deductions += monthly_tds
            net_salary -= monthly_tds

            salary_data = {
                'employee': employee,
                'payroll': self.payroll_org,
                'month': self.month,
                'financial_year': self.financial_year,
                'total_days_of_month': attendance.total_days_of_month,
                'lop': attendance.loss_of_pay,
                'paid_days': total_working_days,
                'ctc': salary_record.annual_ctc,
                'gross_salary': gross_salary,
                'earned_salary': round(earned_salary),
                'basic_salary': round(component_amounts['basic']),
                'hra': round(component_amounts['hra']),
                'conveyance_allowance': round(component_amounts.get('conveyance_allowance', 0)),
                'travelling_allowance': round(component_amounts.get('travelling_allowance', 0)),
                'commission': round(component_amounts.get('commission', 0)),
                'children_education_allowance': round(component_amounts.get('children_education_allowance', 0)),
                'overtime_allowance': round(component_amounts.get('overtime_allowance', 0)),
                'transport_allowance': round(component_amounts.get('transport_allowance', 0)),
                'special_allowance': round(component_amounts['special_allowance']),
                'bonus': round(component_amounts['bonus']),
                'other_earnings': 0 if 0 <= component_amounts['other_earnings'] < 1 else round(
                    component_amounts['other_earnings']),
                'benefits_total': benefits_total,
                'bonus_incentive': round(total_bonus_amount),
                'epf': round(epf_value),
                'esi': round(esi),
                'pt': pt_amount,
                'monthly_fixed_tds': round(monthly_fixed_tds),
                'tds': round(monthly_tds),
                'tds_ytd': round(tds_ytd),
                'annual_tds': round(annual_tds),
                'loan_emi': round(emi_deduction),
                'other_deductions': round(other_deductions),
                'total_deductions': round(total_deductions),
                'net_salary': int(round(net_salary)),
                'is_active': True,
                'notes': "Salary processed from script",
                'other_deductions_breakdown': other_deductions_breakdown,
                'other_earnings_breakdown': component_amounts['other_earnings_breakdown'],
            }
            existing_record = EmployeeSalaryHistory.objects.filter(
                employee=employee,
                payroll=self.payroll_org,
                financial_year=self.financial_year,
                month=self.month
            ).first()

            if existing_record:
                for field, value in salary_data.items():
                    setattr(existing_record, field, value)
                existing_record.save()
            else:
                EmployeeSalaryHistory.objects.create(**salary_data)


class AllOrgPayrollProcessor:
    def __init__(self, financial_year, month):
        self.financial_year = financial_year
        self.month = month

    def run(self):
        payroll_orgs = PayrollOrg.objects.all()
        failed_orgs = []
        success_orgs = []

        for org in payroll_orgs:
            try:
                processor = EmployeeSalaryProcessor(org, self.financial_year, self.month)
                processor.process()
                success_orgs.append(org.business.nameOfBusiness)
            except Exception as e:
                error_trace = traceback.format_exc()
                failed_orgs.append({
                    "org_id": org.id,
                    "org_name": org.business.nameOfBusiness,
                    "error": str(e),
                    "traceback": error_trace
                })

        # ✅ After processing all orgs, send summary email
        self.send_summary_email(success_orgs, failed_orgs)

        if failed_orgs:
            return Response({
                "message": "Payroll processing completed with some errors.",
                "successfully_processed_orgs": success_orgs,
                "failed_orgs": failed_orgs
            }, status=status.HTTP_207_MULTI_STATUS)  # 207: Multi-Status (partial success)
        else:
            return Response({
                "message": "Payroll processing completed for all Payroll Orgs.",
                "successfully_processed_orgs": success_orgs
            }, status=status.HTTP_200_OK)

    def send_summary_email(self, success_orgs, failed_orgs):
        try:
            ses_client = boto3.client(
                'ses',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )

            subject = "✅ Payroll Summary Report"
            body = "Payroll task has completed.\n\n"
            body += f"✅ Successful Orgs ({len(success_orgs)}):\n" + "\n".join(success_orgs) + "\n\n"

            if failed_orgs:
                body += f"❌ Failed Orgs ({len(failed_orgs)}):\n"
                for fail in failed_orgs:
                    body += f"- {fail['org_name']} (Error: {fail['error']})\n"

            response = ses_client.send_email(
                Source='admin@tarafirst.com',
                Destination={
                    'ToAddresses': ['saikiranmekala@tarafirst.com'],
                },
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Text': {'Data': body, 'Charset': 'UTF-8'}}
                }
            )
            print("📧 Summary email sent! Message ID:", response['MessageId'])

        except (BotoCoreError, ClientError) as e:
            print("❌ Failed to send summary email:", str(e))

