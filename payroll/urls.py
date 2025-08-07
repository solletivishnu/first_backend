from django.urls import path
from . import views
from . import employee_management
from . import generate_salary_upload_template
from . import bulk_employee_upload
from . import bulk_salary_details_upload
from . import payroll_workflow
from . import attendance_controller
from . import employeecredentials
from . import face_recognition
from . import leavemanagement
from . import employee_education
from . import holidays
from . import employee_salary_details
# from . import employee_dashboard

urlpatterns = [
    # URL for listing and creating PayrollOrg instances
    path('orgs/', views.PayrollOrgList.as_view(), name='payroll_org_list'),

    # URL for retrieving, updating, or deleting a specific PayrollOrg by its ID
    path('orgs/<int:pk>/', views.PayrollOrgDetail.as_view(), name='payroll_org_detail'),

    # URL for retrieving, updating, or deleting a specific PayrollOrg by its ID
    path('update-payroll-org/<int:business_id>/', views.update_payroll_org, name='update_payroll_org'),

    # URL for clearing the logo field of a PayrollOrg instance
    path('clear-payroll-org-logo/<int:pk>/', views.clear_payroll_org_logo, name='clear_payroll_org_logo'),

    # path('business-payroll/<int:business_id>/', views.PayrollOrgBusinessDetail.as_view(), name='payroll-org-detail'),

    path('business-payroll/<int:business_id>/', views.PayrollOrgBusinessDetailView.as_view(),
         name='payroll-org-business-detail'),

    path('payroll-setup-status', views.business_payroll_check, name='business_payroll_check'),

    # URL for listing and creating WorkLocation instances
    path('work-locations/', views.work_location_list, name='work_location_list'),

    path('work-locations/bulk-upload/', views.bulk_work_location_upload, name='bulk_work_location_upload'),

    # URL for creating a new WorkLocation
    path('work-locations/create/', views.work_location_create, name='work_location_create'),

    # URL for retrieving, updating, or deleting a specific WorkLocation by its ID
    path('work-locations/<int:pk>/', views.work_location_detail, name='work_location_detail'),

    # URL for updating a specific WorkLocation by its ID
    path('work-locations/update/<int:pk>/', views.work_location_update, name='work_location_update'),

    # URL for deleting a specific WorkLocation by its ID
    path('work-locations/delete/<int:pk>/', views.work_location_delete, name='work_location_delete'),

    # URL for downloading templates
    path('download-template/xlsx', views.download_template_xlsx, name='download-template-xlsx'),
    path('download-template/csv', views.download_template_csv, name='download-template-csv'),

    # URL for listing and creating Department instances
    path('departments/', views.department_list, name='department_list'),

    # URL for retrieving, updating, or deleting a specific Department by its ID
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),

    path('departments/bulk-department-upload/', views.bulk_department_upload, name='bulk_department_upload'),


    # URL for listing and creating Designation instances
    path('designations/', views.designation_list, name='designation_list'),

    # URL for retrieving, updating, or deleting a specific Designation by its ID
    path('designations/<int:pk>/', views.designation_detail, name='designation_detail'),

    path('designations/bulk-designations-upload/', views.bulk_designation_upload, name='bulk_designation_upload'),

    path('epf', views.epf_list, name='epf_list'),
    path('epf/<int:pk>', views.epf_detail, name='epf_detail'),

    # ESI Endpoints
    path('esi', views.esi_list, name='esi_list'),
    path('esi/<int:pk>', views.esi_detail, name='esi_detail'),

    # URL for listing and creating PF records
    path('pt', views.pt_list, name='pf_list'),

    # URL for retrieving, updating, or deleting a specific PF record by its ID
    path('pt/<int:pk>', views.pt_detail, name='pf_detail'),

    # URL for listing and creating Earnings records

    path('earnings', views.earnings_list, name='earnings_list'),

    path('earnings-in-payslip', views.earnings_in_payslip, name='earnings-in-payslip'),

    # URL for retrieving, updating, or deleting a specific Earnings record by its ID
    path('earnings/<int:pk>', views.earnings_detail, name='earnings_detail'),

    path('deductions/', views.deductions_list_create, name='deduction-list-create'),
    path('deductions/<int:id>/', views.deduction_detail, name='deduction-detail'),

    # Reimbursement Endpoints
    path('reimbursements/', views.reimbursement_list_create, name='reimbursement-list-create'),
    path('reimbursements/<int:id>/', views.reimbursement_detail, name='reimbursement-detail'),

    # Benefit Endpoints
    path('benefits/', views.benefits_list_create, name='benefit-list-create'),
    path('benefits/<int:id>/', views.benefits_detail_update_delete, name='benefit-detail'),

    # Salary Template Endpoints
    path('salary-templates', views.salary_template_list_create, name='salary_template_list_create'),
    path('salary-templates/<int:template_id>', views.salary_template_detail_update_delete,
         name='salary_template_detail_update_delete'),

    # pay-schedules Endpoints
    path('pay-schedules',  views.pay_schedule_list_create, name='pay_schedule_list_create'),
    path('pay-schedules/<int:schedule_id>',  views.pay_schedule_detail_update_delete,
         name='pay_schedule_detail_update_delete'),

    path('leave-management', views.leave_management_list_create, name='leave-management-list-create'),
    path('leave-management/<int:leave_id>', views.leave_management_detail_update_delete,
         name='leave-management-detail-update-delete'),

    # Holiday Management URLs
    path('holiday-management', views.holiday_management_list_create, name='holiday-management-list-create'),
    path('holiday-management-filter', views.holiday_management_filtered_list, name='holiday-management-filtered-list'),
    path('holiday-management/<int:holiday_id>', views.holiday_management_detail_update_delete,
         name='holiday-management-detail-update-delete'),

    path('employees', views.employee_list, name='employee-list'),
    path('employees/<int:pk>', views.employee_detail, name='employee-detail'),

    path('employee-salary', views.employee_salary_list, name='employee-salary-list'),
    path('employee-salary/<int:pk>', views.employee_salary_detail, name='employee-salary-detail'),

    path('employee-personal-details', views.employee_personal_list, name='employee-personal-list'),
    path('employee-personal-details/<int:pk>', views.employee_personal_detail, name='employee-personal-detail'),

    path('employee-bank-details', views.employee_bank_list, name='employee-bank-list'),
    path('employee-bank-details/<int:pk>', views.employee_bank_detail, name='employee-bank-detail'),

    path('salary-benefits-details/<int:payroll_id>', views.get_payroll_details, name='payroll-details'),

    path("calculate-payroll",  views.calculate_payroll, name="calculate_payroll"),

    path('new-employees', views.new_employees_list, name='new-employees-list'),

    path('employee-exit', views.employee_exit_list, name='employee-exit-list'),  # List or Create
    path('employee-exit/<int:pk>', views.employee_exit_detail, name='employee-exit-detail'),

    path('payroll-exit-settlement', views.payroll_exit_settlement_details, name='payroll-exit-settlement-details'),

    path('advance-loans', views.advance_loan_list, name='advance-loan-list'),  # List or Create
    path('advance-loans/<int:pk>', views.advance_loan_detail, name='advance-loan-detail'),  # Retrieve, Update, Delete

    path('payroll-advance-summary', views.payroll_advance_loans, name='payroll-advance-loans'),

    path('employee-attendance', views.employee_attendance_list, name='employee_attendance_list'),
    path('employee-attendance/<int:pk>', views.employee_attendance_detail, name='employee_attendance_detail'),

    path('employee_attendance_automate', views.generate_next_month_attendance, name='generate-next-month-attendance'),

    path('employee_attendance_current_month_automate', views.generate_current_month_attendance,
         name='generate-current-month-attendance'),

    path('employee_attendance_filtered', views.employee_attendance_filtered, name='employee_attendance_filtered'),

    # Employee Monthly Salary calculation
    path('calculate-employee-monthly-salary', views.calculate_employee_monthly_salary,
         name='calculate-employee-monthly-salary'),

    # Employee Monthly Detail Salary calculation
    path('detail_employee_payroll_salary', views.detail_employee_monthly_salary,
         name='detail-employee-monthly-salary'),

    path('monthly-salary-details-of-employees', views.monthly_salary_details_of_employees,
         name='monthly-salary-details-of-employees'),
    path('download-salary-report', views.download_salary_report, name='download-salary-report'),

    path('employee-monthly-salary-template', views.employee_monthly_salary_template,
         name='employee-monthly-salary-template'),

    path('payroll-summary-view', views.payroll_summary_view, name='payroll-summary-view'),

    path('payroll_financial-year-summary', views.get_financial_year_summary, name='financial_year_summary'),

    path('bonus-incentives/by-payroll-month', views.bonus_incentive_list, name='bonus-incentive-list'),

    path('bonus-incentives', views.bonus_incentive_create, name='bonus-incentive-list-all'),

    path('bonus-incentives/<int:pk>', views.bonus_incentive_detail, name='bonus-incentive-detail'),

    # path('employee-salaries', views.active_employee_salaries, name='active-employee-salaries'),
    
    path("employee-tds",views.employee_tds_list,name="employee-tds-list"),
    
    path("employee-tds/<int:pk>",views.employee_tds_detail,name="employee-tds-detail"),

    path("salary-revision", views.salary_revision_list, name="salary-revision-list"),

    path("employees/delete/", views.delete_employees_by_payroll, name="delete-employees-by-payroll"),

    path('download-template/<int:payroll_id>/', employee_management.generate_employee_upload_template,
         name='download_employee_template'),

    path('employee-salary-template/<int:payroll_id>/',
         generate_salary_upload_template.generate_salary_upload_template, name='salary-template'),

    path('employees/upload/', bulk_employee_upload.upload_employee_excel, name='upload-employee-excel'),

    path('employee-salary-bulk-upload/', bulk_salary_details_upload.upload_employee_salary_excel, name='upload-bulk-salary-data'),

    path('payroll-workflows/', payroll_workflow.payroll_workflow_list),
    path('payroll-workflows/create/', payroll_workflow.payroll_workflow_create),
    path('payroll-workflows/<int:pk>/update/', payroll_workflow.payroll_workflow_update),
    path('payroll-workflows/<int:pk>/delete/', payroll_workflow.payroll_workflow_delete),
    path('payroll-workflows/detail-or-create/', payroll_workflow.payroll_workflow_detail_or_create),

    # Manual check-in/check-out

    path('manual-checkin/', attendance_controller.manual_check_in, name='manual-check-in'),
    path('manual-checkout/', attendance_controller.manual_check_out, name='manual-check-out'),

    #Geo Location check-in/check-out
    path('geo-location-check-in/', attendance_controller.geo_location_check_in, name='geo-location-check-in'),
    path('geo-location-check-out/', attendance_controller.geo_location_check_out, name='geo-location-check-out'),

    # Face recognition check-in/check-out
    # path('face-checkin/', attendance_controller.face_checkin_checkout, name='face-checkin'),

    # Get today's attendance
    path('today/', attendance_controller.today_attendance_status, name='today-attendance'),

    # Monthly report
    path('monthly-report/', attendance_controller.truetime_monthly_view, name='monthly-report'),
    path('weekly-report/', attendance_controller.truetime_weekly_view, name='weekly-report'),
    path('date-wise-report/', attendance_controller.truetime_datewise_view, name='date-wise-report'),


    path("credentials/", employeecredentials.credentials_list_create, name="credentials-list-create"),
    path("credentials/<int:pk>/", employeecredentials.credentials_detail, name="credentials-detail"),

    # ───────────── Employee Login (JWT) ─────────────
    path("auth/employee-login/", employeecredentials.employee_login, name="employee-login"),

    # Capture employee images
    path("upload-employee-images/", face_recognition.upload_employee_images, name="upload-employee-image"),

    # FaceRecognition Check-In
    path("face-recognition-check-in/", face_recognition.face_recognition_check_in, name="face-recognition-check-in"),
    path("face-recognition-check-out/", face_recognition.face_recognition_check_out, name="face-recognition-check-out"),
    path("attendance-summary-view/", face_recognition.attendance_summary_view, name="attendance-summary-view"),
    path('process-single-org/', views.process_single_payroll_org, name='process-single-payroll-org'),

    # Leave Approval and Rejection In Employee Portal
    path('apply/', leavemanagement.apply_leave, name='apply-leave'),
    path('list/', leavemanagement.get_leave_applications, name='get-leaves'),
    path('month/<int:year>/<int:month>/', leavemanagement.get_monthly_leaves, name='monthly-leaves'),
    path('current-month/', leavemanagement.get_current_month_leaves, name='current-month-leaves'),
    path('summary/', leavemanagement.get_leave_summary, name='yearly-summary'),
    path('summary/<int:year>/', leavemanagement.get_leave_summary, name='yearly-summary'),
    path('leave/action/<int:leave_id>/', leavemanagement.handle_leave_action, name='leave-action'),
    path('reject/<int:pk>/', leavemanagement.reject_leave, name='reject-leave'),
    path('cancel/<int:pk>/', leavemanagement.cancel_leave, name='cancel-leave'),
    # Employee Leave Balance
    path('my-leave-balances/', leavemanagement.get_my_leave_balances, name='my_leave_balances'),

    # Employee Education Endpoints
    path('employee-education/', employee_education.employee_education_list_create, name='employee-education-list-create'),
    path('employee-education/<int:education_id>/', employee_education.employee_education_detail,
         name='employee-education-detail'),
    path('employee-profile/', employee_education.employee_profile_details, name='employee-profile'),

    # Holiday Calendar Endpoints
    path('monthly-holidays/', holidays.get_month_wise_holiday_calendar, name='monthly-holidays'),
    path('holiday-calendar/', holidays.get_yearly_holiday_calendar, name='holiday-calendar'),

    # Employee Salary Details Endpoints
    path('employee-payslip/', employee_salary_details.employee_payslip_details, name='generate-payslip'),
    path('employee-ytd-details/', employee_salary_details.get_month_and_ytd_salary_data, name='generate-ytd-payslip'),
    path('pf-breakdown/', employee_salary_details.get_pf_breakdown, name='pf-breakdown'),
    path('employee-payslips-by-financial-year/', employee_salary_details.get_employee_financial_year_payslip_details,
         name='employee-financial-year-payslip-details'),


    # path('tds-summary/', employee_dashboard.tds_summary_view, name='tds-summary-view'),
]
