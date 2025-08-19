from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from .helpers import *
from usermanagement.models import *
from datetime import date
from collections import OrderedDict
from django.db.models.signals import pre_save, post_save
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from django.contrib.auth.hashers import make_password, check_password


def validate_pincode(value):
    if len(str(value)) != 6:  # Assuming 6-digit pin codes
        raise ValidationError(f"{value} is not a valid pin code.")


class PayrollOrg(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Use auto_now_add for creation timestamp
    sender_email = models.EmailField(max_length=120, null=True, blank=True)
    filling_address_location_name = models.CharField(max_length=120, null=True, blank=True,default="Head Office")
    filling_address_line1 = models.CharField(max_length=150, null=True, blank=True)
    filling_address_line2 = models.CharField(max_length=150, null=True, blank=True)
    filling_address_state = models.CharField(max_length=150, null=True, blank=True)
    filling_address_city = models.CharField(max_length=150, null=True, blank=True)
    filling_address_pincode = models.PositiveIntegerField(null=True, validators=[validate_pincode]) # No max_length
    work_location = models.BooleanField(default=False)
    department = models.BooleanField(default=False)
    designation = models.BooleanField(default=False)
    # JSONFields should have a default empty dictionary
    statutory_component = models.BooleanField(default=False)
    salary_component = models.BooleanField(default=False)
    salary_template = models.BooleanField(default=False)
    pay_schedule = models.BooleanField(default=False)
    leave_management = models.BooleanField(default=False)
    holiday_management = models.BooleanField(default=False)
    employee_master = models.BooleanField(default=False)


    def to_representation(self, instance):
        """Convert OrderedDict to dict before returning JSON."""
        data = super().to_representation(instance)
        if isinstance(data.get("organisation_address"), OrderedDict):
            data["organisation_address"] = dict(data["organisation_address"])  # Convert OrderedDict to dict
        return data

    def __str__(self):
        return f"PayrollOrg {self.business.id}"


@receiver(pre_save, sender=PayrollOrg)
def check_business_head_office(sender, instance, **kwargs):
    """ Prevent PayrollOrg creation if business.headOffice is empty """
    if not instance.business.headOffice or instance.business.headOffice in [{}, OrderedDict()]:
        raise ValidationError("Business headOffice cannot be empty. Please set headOffice before creating PayrollOrg.")


@receiver(post_save, sender=PayrollOrg)
def create_work_location(sender, instance, created, **kwargs):
    """Automatically create a Work Location based on Business Head Office details."""
    if created:  # Ensure it runs only when PayrollOrg is created
        business = instance.business

        # Extracting head_office details from JSONField
        head_office = business.headOffice or {}  # Default to empty dict if None

        WorkLocations.objects.create(
            payroll=instance,
            location_name="Head Office",
            address_line1=head_office.get("address_line1"),
            address_line2=head_office.get("address_line2"),
            address_state=head_office.get("state"),
            address_city=head_office.get("city"),
            address_pincode=head_office.get("pincode"),
        )


class WorkLocations(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='work_locations')
    created_at = models.DateTimeField(auto_now_add=True)
    location_name = models.CharField(max_length=120)
    address_line1 = models.CharField(max_length=150, null=True, blank=True)
    address_line2 = models.CharField(max_length=150, null=True, blank=True)
    address_state = models.CharField(max_length=150, null=True, blank=True)
    address_city = models.CharField(max_length=150, null=True, blank=True)
    address_pincode = models.PositiveIntegerField(null=True, validators=[validate_pincode])

    class Meta:
        unique_together = ('payroll', 'location_name')

    def __str__(self):
        return self.location_name


@receiver(post_save, sender=WorkLocations)
def create_professional_tax(sender, instance, created, **kwargs):
    """Automatically create a Professional Tax record when a new work location is added."""
    if created:  # Ensure it runs only when a new WorkLocation is created
        PT.objects.create(
            payroll=instance.payroll,  # Assign the payroll
            work_location=instance,  # Assign the new work location
            pt_number=None,  # Keep it null by default
            deduction_cycle="Monthly",  # Default deduction cycle
        )


class Departments(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='departments')
    dept_code = models.CharField(max_length=150)
    dept_name = models.CharField(max_length=150)
    description = models.CharField(max_length=220, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll', 'dept_code'], name='unique_dept_code_per_payroll'),
            models.UniqueConstraint(fields=['payroll', 'dept_name'], name='unique_dept_name_per_payroll'),
        ]

    def __str__(self):
        return f"{self.dept_name}"


class Designation(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='designations')
    designation_name = models.CharField(max_length=150)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll', 'designation_name'], name='unique_designation_per_payroll'),
        ]

    def __str__(self):
        return self.designation_name


class EPF(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='epf_details')
    epf_number = models.CharField(max_length=100, null= True, blank=False, default=None)  # Adjust max_length as needed
    employee_contribution_rate = models.CharField(max_length=240, null=True, blank=False,default=None)
    employer_contribution_rate = models.CharField(max_length=240, null=True, blank=False, default=None)
    employer_edil_contribution_in_ctc = models.BooleanField()  # EDLI contribution included
    # in CTC Employees' Deposit Linked Insurance
    include_employer_contribution_in_ctc = models.BooleanField(default=False)
    admin_charge_in_ctc = models.BooleanField(default=False)  # Admin charge included in CTC
    allow_employee_level_override = models.BooleanField(default=False)  # Can employee override PF?
    prorate_restricted_pf_wage = models.BooleanField(default=False)  # Prorate restricted PF wage?
    apply_components_if_wage_below_15k = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return f"EPF Details for Payroll: {self.payroll.business.nameOfBusiness} (EPF No: {self.epf_number})"


class ESI(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='esi_details')
    esi_number = models.CharField(max_length=100, null=True, blank=True)  # Adjust max_length as needed
    employee_contribution = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)  # e.g., 0.75
    employer_contribution = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)  # e.g., 3.25
    include_employer_contribution_in_ctc = models.BooleanField()  # Include employer contribution in CTC?
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return f"ESI Details for Payroll: {self.payroll.business.nameOfBusiness} (ESI No: {self.esi_number})"


class PT(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='pt_details')
    work_location = models.ForeignKey('WorkLocations', on_delete=models.CASCADE, related_name='pt_records')
    pt_number = models.CharField(max_length=100, null=True, blank=True)  # Can be null by default
    slab = JSONField(default=list, blank=True)  # Stores PT slab dynamically
    deduction_cycle = models.CharField(max_length=20, default="Monthly")
    is_disabled = models.BooleanField(default=False)  # Indicates if PT is disabled for this payroll

    class Meta:
        unique_together = ('payroll', 'work_location')  # Ensures one PT per payroll-location pair

    def __str__(self):
        return (f"PT Details - Payroll: {self.payroll.business.nameOfBusiness}, "
                f"Location: {self.work_location.location_name}")

    def save(self, *args, **kwargs):
        """
        Assign the PT slab dynamically based on the state of the work location.
        """
        state = self.work_location.address_state  # Assuming `state` is a field in WorkLocations
        self.slab = self.get_slab_for_state(state)  # Fetch the correct slab
        super().save(*args, **kwargs)

    @staticmethod
    def get_slab_for_state(state):
        """
        Returns the PT slab with only Monthly Salary and Professional Tax.
        """
        slabs = {
            "Telangana": [
                {"Monthly Salary (₹)": "Up to 15,000", "Professional Tax (₹ per month)": "Nil"},
                {"Monthly Salary (₹)": "15,001 to 20,000", "Professional Tax (₹ per month)": "150"},
                {"Monthly Salary (₹)": "20,001 to 25,000", "Professional Tax (₹ per month)": "200"},
                {"Monthly Salary (₹)": "25,001 and above", "Professional Tax (₹ per month)": "250"},
            ],
            "Karnataka": [
                {"Monthly Salary (₹)": "Up to 15,000", "Professional Tax (₹ per month)": "Nil"},
                {"Monthly Salary (₹)": "Above 15,000", "Professional Tax (₹ per month)": "200"},
            ],
            "Andhra Pradesh": [
                {"Monthly Salary (₹)": "Up to 15,000", "Professional Tax (₹ per month)": "Nil"},
                {"Monthly Salary (₹)": "15,001 to 20,000", "Professional Tax (₹ per month)": "150"},
                {"Monthly Salary (₹)": "20,001 to 25,000", "Professional Tax (₹ per month)": "200"},
                {"Monthly Salary (₹)": "25,001 and above", "Professional Tax (₹ per month)": "250"},
            ],
        }
        return slabs.get(state, [])


class Earnings(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='earnings')
    component_name = models.CharField(max_length=150)  # Name of the earning
    component_type = models.CharField(max_length=60)  # Type of earning
    calculation_type = JSONField(default=dict)  # Stores calculation details
    is_active = models.BooleanField(default=True)  # Whether the earning is active
    is_part_of_employee_salary_structure = models.BooleanField(default=False)  # Part of salary structure
    is_taxable = models.BooleanField(default=True)  # Taxable earning
    is_pro_rate_basis = models.BooleanField(default=False)  # Pro-rata basis
    is_fbp_component = models.BooleanField(default=False)  # Flexible benefit plan
    includes_epf_contribution = models.BooleanField(default=False)  # EPF contribution
    includes_esi_contribution = models.BooleanField(default=False)  # ESI contribution
    is_included_in_payslip = models.BooleanField(default=True)  # Included in payslip
    tax_deduction_preference = models.CharField(max_length=120, null=True, blank=True)
    is_scheduled_earning = models.BooleanField(default=True)
    pf_wage_less_than_15k = models.BooleanField(default=False)
    always_consider_epf_inclusion = models.BooleanField(default=False)

    def clean(self):
        # Ensure tax_deduction_preference is required if component_name is "Bonus"
        if self.component_name.lower() == "bonus" and not self.tax_deduction_preference:
            raise ValidationError(
                {"tax_deduction_preference": "This field is required when component name is 'Bonus'."}
            )

    def save(self, *args, **kwargs):
        # Call the clean method to validate the model before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Earning: {self.component_name} ({self.component_type})"


class Benefits(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='benefits')
    benefit_type = models.CharField(max_length=150)  # Type of benefit (e.g., health insurance, transport)
    associated_with = models.CharField(max_length=60)  # What the benefit is linked to
    payslip_name = models.CharField(max_length=60, unique=True) # Display name in the payslip
    is_active = models.BooleanField(default=True)  # Whether the benefit is active
    is_pro_rated = models.BooleanField(default=False)  # Indicates if the benefit is pro-rated
    includes_employer_contribution = models.BooleanField(default=False)  # Whether employer contributes
    frequency = models.CharField(max_length=120)  # Frequency of benefit (e.g., monthly, yearly)

    def __str__(self):
        return f"{self.benefit_type} ({self.payslip_name})"


class Deduction(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='deductions')
    component_type = models.CharField(max_length=60, default='Fixed')
    deduction_name = models.CharField(max_length=150)  # Type of deduction (e.g., tax, insurance)
    calculation_type = JSONField(default=dict)
    includes_epf_contribution = models.BooleanField(default=False)  # EPF contribution
    includes_esi_contribution = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.deduction_name} "


class Reimbursement(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='reimbursements')
    reimbursement_type = models.CharField(max_length=150)  # Type of reimbursement (e.g., medical, travel)
    payslip_name = models.CharField(max_length=60, unique=True)  # Display name in the payslip (unique)
    include_in_flexible_benefit_plan = models.BooleanField()  # Whether it should be included in flexible benefit plan
    unclaimed_reimbursement = models.BooleanField()  # Whether the reimbursement is unclaimed
    amount_value = models.IntegerField()  # The reimbursement amount value
    is_active = models.BooleanField(default=True)  # Whether the reimbursement is active

    def __str__(self):
        return f"{self.reimbursement_type} ({self.payslip_name})"


class SalaryTemplate(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='salary_templates')
    template_name = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=250, null=True, blank=True)
    annual_ctc = models.IntegerField()

    # Fields for earnings, benefits, deductions that should contain specific structures
    earnings = JSONField(default=list, blank=True)
    gross_salary = JSONField(default=dict, blank=True)
    benefits = JSONField(default=list, blank=True)
    total_ctc = JSONField(default=dict, blank=True)
    deductions = JSONField(default=list, blank=True)
    net_salary = JSONField(default=dict, blank=True)

    def clean(self):
        # Ensure earnings, benefits, and deductions contain required fields when present
        for section in [self.earnings, self.benefits, self.deductions]:
            for item in section:
                if not isinstance(item, dict):
                    raise ValidationError(f"Each item in {section} must be a dictionary.")
                if ('component_name' not in item or 'calculation_type' not in item or 'monthly'
                        not in item or 'annually' not in item):
                    raise ValidationError(f"Each item in {section} "
                                          f"must contain 'component_name', 'calculation_type', "
                                          f"'monthly', and 'annually'.")

        # Validate structure for gross_salary, total_ctc, and net_salary
        for field_name in ['gross_salary', 'total_ctc', 'net_salary']:
            field_data = getattr(self, field_name)
            if not isinstance(field_data, dict):
                raise ValidationError(f"{field_name} must be a dictionary containing 'monthly' and 'annually'.")
            if 'monthly' not in field_data or 'annually' not in field_data:
                raise ValidationError(f"{field_name} must contain 'monthly' and 'annually' fields.")

    def save(self, *args, **kwargs):
        # Call clean method to validate the model before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary Template: {self.template_name}"


class PaySchedule(BaseModel):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='payroll_scheduling')
    payroll_start_month = models.CharField(max_length=60, null=False, blank=False)
    sunday = models.BooleanField(default=False)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    second_saturday = models.BooleanField(default=False)
    fourth_saturday = models.BooleanField(default=False)

    def clean(self):
        """ Ensure at least two days are selected """
        selected_days = sum([
            self.sunday, self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.second_saturday, self.fourth_saturday
        ])


    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class LeaveManagement(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='leave_managements')
    name_of_leave = models.CharField(max_length=120)
    code = models.CharField(max_length=20, null=True, blank=True, default=None)  # Ensuring code uniqueness
    leave_type = models.CharField(max_length=60)  # Renamed from `type` to `leave_type`
    employee_leave_period = models.CharField(max_length=80, default='-')
    number_of_leaves = models.FloatField(null=True, blank=True, default=None)
    pro_rate_leave_balance_of_new_joinees_based_on_doj = models.BooleanField(default=False)
    reset_leave_balance = models.BooleanField(default=False)
    reset_leave_balance_type = models.CharField(max_length=20, default=None, null=True)
    carry_forward_unused_leaves = models.BooleanField(default=False)
    max_carry_forward_days = models.IntegerField(default=None, null=True)
    encash_remaining_leaves = models.BooleanField(default=False)
    encashment_days = models.IntegerField(default=None, null=True)

    class Meta:
        verbose_name = "Leave Management"
        verbose_name_plural = "Leave Managements"

    def __str__(self):
        return f"{self.name_of_leave} ({self.code})"


class HolidayManagement(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='holiday_managements')
    financial_year = models.CharField(max_length=20)  # Format: "2024-2025"
    holiday_name = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)  # Optional
    applicable_for = models.ManyToManyField('WorkLocations', related_name='applicable_holidays', blank=True)

    class Meta:
        verbose_name = "Holiday Management"
        verbose_name_plural = "Holiday Managements"

    def __str__(self):
        return f"{self.holiday_name} ({self.financial_year})"


class EmployeeManagement(BaseModel):
    GENDER_CHOICES = [
        ('male', 'male'),
        ('female', 'female'),
        ('others', 'others'),
    ]

    level_choices = [
        ('0', '0 - CEO / Director / Executive'),
        ('1', '1 - Vice President / General Manager'),
        ('2', '2 - HR Manager'),
        ('3', '3 - Department Manager'),
        ('4', '4 - Team Lead / Project Lead'),
        ('5', '5 - Employee / Trainee / Intern'),
    ]

    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='employee_managements')
    first_name = models.CharField(max_length=120, null=False, blank=False)
    middle_name = models.CharField(max_length=80, null=True, blank=True, default=None)
    last_name = models.CharField(max_length=80, null=False, blank=False)
    associate_id = models.CharField(max_length=120, blank=False, null=False)
    doj = models.DateField()
    work_email = models.EmailField()
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='male')
    work_location = models.ForeignKey('WorkLocations', on_delete=models.CASCADE,
                                      related_name='employee_work_location')
    designation = models.ForeignKey('Designation', on_delete=models.CASCADE, related_name='employee_designation')
    department = models.ForeignKey('Departments', on_delete=models.CASCADE, related_name='employee_department')
    enable_portal_access = models.BooleanField(default=False)
    statutory_components = models.JSONField()
    employee_level = models.CharField(max_length=120, choices=level_choices, null=True, blank=True, default='5')
    employee_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.associate_id} ({self.gender})"


class EmployeeReportingManager(models.Model):
    employee = models.OneToOneField(
        'EmployeeManagement',
        on_delete=models.CASCADE,
        related_name='reviewing_team'
    )
    reporting_manager = models.ForeignKey(
        'EmployeeManagement',
        on_delete=models.CASCADE,
        related_name='reported_by'
    )
    head_of_department = models.ForeignKey(
        'EmployeeManagement',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='head_of_department'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Custom validation: allow self-reference for lower levels/departments."""
        level = int(self.employee.level)
        department = self.employee.department.lower()  # assuming CharField

        allow_self = level in [0, 1]

        if not allow_self:
            if self.reporting_manager == self.employee:
                raise ValidationError("Self cannot be the reviewing manager for levels above 2.")
            if self.head_of_department == self.employee:
                raise ValidationError("Self cannot be the head of department for levels above 2.")

    def __str__(self):
        return f"{self.employee.associate_id} - Reviewing Team"


@receiver(post_save, sender=EmployeeManagement)
def allocate_pro_rated_leave(sender, instance, created, **kwargs):
    """Automatically allocate leave balance based on the financial year when a new employee is created."""
    if created:
        leave_policies = LeaveManagement.objects.filter(payroll=instance.payroll)

        # Automatically calculate financial year based on the current date
        today = date.today()
        if today.month >= 4:
            start_year = today.year
            end_year = today.year + 1
        else:
            start_year = today.year - 1
            end_year = today.year

        leave_period_start = date(start_year, 4, 1)
        leave_period_end = date(end_year, 3, 31)

        for leave in leave_policies:
            total_leaves = leave.number_of_leaves
            pro_rated_leave = total_leaves  # Default full allocation

            # Calculate remaining months in the financial year
            if instance.doj < leave_period_start:
                remaining_months = 12
            else:
                remaining_months = (leave_period_end.year - instance.doj.year) * 12 + (
                            leave_period_end.month - instance.doj.month) + 1

            if leave.employee_leave_period == "Monthly":
                # If leave is allocated monthly, multiply remaining months by number_of_leaves
                pro_rated_leave = total_leaves * remaining_months

            elif leave.employee_leave_period == "Annually":
                # If leave is allocated annually, divide annual leave by remaining months
                pro_rated_leave = round((total_leaves / 12) * remaining_months)

            # Create Leave Balance Entry
            EmployeeLeaveBalance.objects.create(
                employee=instance,
                leave_type=leave,
                leave_entitled=pro_rated_leave,
                leave_remaining=pro_rated_leave,
                financial_year=f"{start_year}-{end_year}"
            )


class EmployeeLeaveBalance(models.Model):
    """Leave Balance Model"""
    employee = models.ForeignKey(EmployeeManagement, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveManagement, on_delete=models.CASCADE, related_name='leave_balances')
    leave_entitled = models.FloatField()  # Total entitled leave
    leave_used = models.FloatField(default=0)  # Leaves taken
    leave_remaining = models.FloatField()  # Auto-calculated
    financial_year = models.CharField(max_length=10, null=False, blank=False)

    def save(self, *args, **kwargs):
        """Auto-calculate remaining leaves before saving."""
        self.leave_remaining = self.leave_entitled - self.leave_used
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.name_of_leave}: {self.leave_remaining} remaining"


class EmployeeSalaryDetails(models.Model):
    employee = models.OneToOneField(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_salary'
    )  # Allows multiple salary records per employee

    annual_ctc = models.IntegerField()

    earnings = models.JSONField(default=list, blank=True)
    gross_salary = models.JSONField(default=dict, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    total_ctc = models.JSONField(default=dict, blank=True)
    deductions = models.JSONField(default=list, blank=True)
    net_salary = models.JSONField(default=dict, blank=True)
    tax_regime_opted = models.CharField(max_length=225, blank=True, null=True, default='new')
    valid_from = models.DateField(auto_now_add=True)  # Salary start date
    valid_to = models.DateField(null=True, blank=True)  # Salary end date (null = current salary)
    created_on = models.DateField(auto_now_add=True)
    created_month = models.IntegerField(editable=False)
    created_year = models.IntegerField(editable=False)
    is_variable_bonus = models.BooleanField(default=False)  # Indicates if the salary includes variable bonus
    variable_bonus = models.JSONField(default=dict, blank=True)  # Stores variable bonus details

    def clean(self):
        """Ensure no open salary record exists before adding a new one."""
        active_salary = EmployeeSalaryDetails.objects.filter(
            employee=self.employee,
            valid_to__isnull=True
        ).exclude(id=self.id).first()

        if active_salary:
            raise ValidationError(
                "An active salary record already exists. Please close the existing record before adding a new one."
            )

        # Validate earnings, benefits, and deductions
        for section_name, section in [('earnings', self.earnings), ('benefits', self.benefits),
                                      ('deductions', self.deductions)]:
            if not isinstance(section, list):
                raise ValidationError(f"{section_name} must be a list.")
            for item in section:
                if not isinstance(item, dict):
                    raise ValidationError(f"Each item in {section_name} must be a dictionary.")
                required_fields = {'component_name', 'calculation_type', 'monthly', 'annually'}
                if not required_fields.issubset(item):
                    raise ValidationError(f"Each item in {section_name} must contain {required_fields}.")

        # Validate structure for gross_salary, total_ctc, and net_salary
        for field_name in ['gross_salary', 'total_ctc', 'net_salary']:
            field_data = getattr(self, field_name)
            if not isinstance(field_data, dict):
                raise ValidationError(f"{field_name} must be a dictionary.")
            if 'monthly' not in field_data or 'annually' not in field_data:
                raise ValidationError(f"{field_name} must contain 'monthly' and 'annually' fields.")

        # Validate variable bonus if marked as included
        if self.is_variable_bonus:
            if not isinstance(self.variable_bonus, dict):
                raise ValidationError("Variable bonus must be a dictionary when 'is_variable_bonus' is True.")

            required_bonus_fields = {'bonus_amount', 'pay_cycle_frequency'}
            if not required_bonus_fields.issubset(self.variable_bonus):
                raise ValidationError(f"Variable bonus must contain {required_bonus_fields}.")

            # Validate pay_cycle_frequency
            valid_frequencies = {'Monthly', 'Quarterly', 'HalfYearly', 'Yearly'}
            frequency = self.variable_bonus.get('pay_cycle_frequency')

            if frequency not in valid_frequencies:
                raise ValidationError(f"Invalid pay_cycle_frequency '{frequency}'. Must be one of {valid_frequencies}.")

            # Validate bonus_amount
            bonus_amount = self.variable_bonus.get('bonus_amount')
            if not isinstance(bonus_amount, (int, float)):
                raise ValidationError("bonus_amount must be a number.")

    def save(self, *args, **kwargs):
        """Ensure the previous salary is closed before adding a new record."""
        # Close the existing active salary before saving the new one
        active_salary = EmployeeSalaryDetails.objects.filter(employee=self.employee, valid_to__isnull=True).exclude(
            id=self.id).first()

        if active_salary:
            active_salary.valid_to = date.today()
            active_salary.save()

        self.clean()  # Validate the model before saving

        # Auto-set created_month and created_year based on created_on (if new object)
        if not self.pk:
            today = self.created_on or date.today()
            self.created_month = today.month
            self.created_year = today.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.associate_id} - {self.valid_from}"


class EmployeeSalaryRevisionHistory(models.Model):
    employee = models.ForeignKey('EmployeeManagement', on_delete=models.CASCADE, related_name='salary_revision_history')
    previous_ctc = models.IntegerField()
    current_ctc =models.IntegerField()
    revision_date = models.DateField(null=True, blank=True)
    revision_month = models.IntegerField(blank=True, null=True)
    revision_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Revision for {self.employee.associate_id} on {self.revision_date}"


@receiver(pre_save, sender=EmployeeSalaryDetails)
def create_salary_revision_history(sender, instance, **kwargs):
    """
    Signal to create or update EmployeeSalaryRevisionHistory when EmployeeSalaryDetails is updated.
    """
    if instance.pk:  # Only for updates, not new records
        try:
            old_instance = EmployeeSalaryDetails.objects.get(pk=instance.pk)
            
            # Check if there's a change in CTC
            if old_instance.annual_ctc != instance.annual_ctc:
                today = datetime.now().date()
                
                # Get payroll_month and payroll_year from instance
                payroll_month = getattr(instance, 'payroll_month', None)
                payroll_year = getattr(instance, 'payroll_year', None)
                
                # If not set, use current month/year
                if payroll_month is None:
                    payroll_month = today.month
                if payroll_year is None:
                    payroll_year = today.year
                
                # Get or create revision history for current month/year
                revision_history, created = EmployeeSalaryRevisionHistory.objects.get_or_create(
                    employee=instance.employee,
                    revision_month=payroll_month,
                    revision_year=payroll_year,
                    defaults={
                        'previous_ctc': old_instance.annual_ctc,
                        'current_ctc': instance.annual_ctc,
                        'revision_date': today,
                    }
                )
                
                # If record exists, update it
                if not created:
                    revision_history.previous_ctc = old_instance.annual_ctc
                    revision_history.current_ctc = instance.annual_ctc
                    revision_history.revision_date = today
                    revision_history.save()
        except EmployeeSalaryDetails.DoesNotExist:
            pass


class EmployeePersonalDetails(BaseModel):
    MARITAL_CHOICES = [
        ('single', 'single'),
        ('married', 'married'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('Unknown', 'Unknown'),
        ('A+', 'A Positive (A+)'),
        ('A-', 'A Negative (A-)'),
        ('B+', 'B Positive (B+)'),
        ('B-', 'B Negative (B-)'),
        ('AB+', 'AB Positive (AB+)'),
        ('AB-', 'AB Negative (AB-)'),
        ('O+', 'O Positive (O+)'),
        ('O-', 'O Negative (O-)'),
    ]

    employee = models.OneToOneField('EmployeeManagement', on_delete=models.CASCADE,
                                 related_name='employee_personal_details')
    dob = models.DateField()
    age = models.IntegerField()
    guardian_name = models.CharField(max_length=120, null=False, blank=False)
    pan = models.CharField(max_length=20, null=True, blank=False, default=None)
    aadhar = models.CharField(max_length=80, null=True, blank=False, default=None)
    address = models.JSONField()
    alternate_contact_number = models.CharField(max_length=40, null=True, blank=True, default=None)
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, default='single', null=True, blank=True)
    blood_group = models.CharField(max_length=15, choices=BLOOD_GROUP_CHOICES, default='O+', null=True, blank=True)

    def clean(self):
        """Validate that alternate contact number is not the same as employee's mobile number."""
        if self.alternate_contact_number and self.employee.mobile_number:
            if self.alternate_contact_number == self.employee.mobile_number:
                raise ValidationError('Alternate contact number cannot be the same as the employee\'s mobile number.')
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.associate_id} ({self.dob})"


class EmployeeBankDetails(BaseModel):
    employee = models.OneToOneField('EmployeeManagement', on_delete=models.CASCADE,
                                    related_name='employee_bank_details')
    account_holder_name = models.CharField(max_length=150, null=False, blank=False)
    bank_name = models.CharField(max_length=150, null=False, blank=False)
    account_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    ifsc_code = models.CharField(max_length=20, null=False, blank=False)
    branch_name = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # To mark active/inactive bank details

    def __str__(self):
        return f"{self.employee.associate_id} - {self.bank_name} ({self.account_number})"


class EmployeeExit(models.Model):
    employee = models.OneToOneField(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_exit_details'
    )
    doe = models.DateField()
    exit_month = models.IntegerField(editable=False, null=True)  # auto-filled
    exit_year = models.IntegerField(editable=False, null=True)   # auto-filled
    exit_reason = models.CharField(max_length=256, null=True, blank=True, default=None)
    regular_pay_schedule = models.BooleanField()
    specify_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True, default='')

    def clean(self):
        if self.regular_pay_schedule and self.specify_date is not None:
            raise ValidationError(
                "If 'regular_pay_schedule' is True, 'specify_date' must be None."
            )
        if not self.regular_pay_schedule and self.specify_date is None:
            raise ValidationError(
                "If 'regular_pay_schedule' is False, 'specify_date' must be provided."
            )

    def save(self, *args, **kwargs):
        self.clean()

        # Auto-assign month and year from `doe`
        if self.doe:
            self.exit_month = self.doe.month
            self.exit_year = self.doe.year

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Exit: {self.employee.first_name} {self.employee.last_name} ({self.doe})"


class AdvanceLoan(models.Model):
    employee = models.ForeignKey(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_advance_loan'
    )
    loan_type = models.CharField(max_length=120, null=False, blank=False)  # Renamed 'type' to 'loan_type' (reserved keyword)
    amount = models.IntegerField()
    no_of_months = models.IntegerField()
    emi_amount = models.IntegerField(editable=False)  # Auto-calculated
    start_month = models.DateField()
    end_month = models.DateField(editable=False)  # Auto-calculated

    def clean(self):
        """Validation: Ensure amount and months are positive."""
        if self.amount <= 0:
            raise ValidationError("Loan amount must be greater than zero.")
        if self.no_of_months <= 0:
            raise ValidationError("Number of months must be greater than zero.")

    def save(self, *args, **kwargs):
        """Auto-calculate EMI and End Month before saving."""
        self.clean()
        self.emi_amount = self.amount // self.no_of_months  # Equal installment
        self.end_month = self.start_month + relativedelta(months=self.no_of_months)  # Auto-calculate end month
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.first_name} - {self.loan_type} Loan ({self.amount})"


class BonusIncentive(models.Model):
    employee = models.ForeignKey(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_bonus_incentive'
    )
    bonus_type = models.CharField(max_length=120, null=False, blank=False)
    amount = models.IntegerField()
    month = models.IntegerField(null=False)
    year = models.IntegerField(null=False, editable=False)
    financial_year = models.CharField(max_length=10, null=False, blank=False)
    remarks = models.TextField(null=True, blank=True, default='')

    def save(self, *args, **kwargs):
        try:
            start_year, end_year = map(int, self.financial_year.split('-'))
            # Determine year based on financial year and month
            if self.month >= 4:
                self.year = start_year
            else:
                self.year = end_year
        except (ValueError, IndexError):
            raise ValueError("Invalid financial_year format. It should be like '2024-2025'")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.first_name} - {self.bonus_type} Bonus ({self.amount})"


class EmployeeAttendance(models.Model):
    """Employee Attendance Tracking Model."""
    employee = models.ForeignKey(EmployeeManagement, on_delete=models.CASCADE, related_name='employee_attendance')
    financial_year = models.CharField(max_length=10, null=False, blank=False)
    month = models.IntegerField(null=False)
    total_days_of_month = models.IntegerField(null=False)
    holidays = models.FloatField(null=False)
    week_offs = models.IntegerField(null=False)
    present_days = models.FloatField(null=False)
    balance_days = models.FloatField(null=False)
    casual_leaves = models.FloatField(null=False)
    sick_leaves = models.FloatField(null=False)
    earned_leaves = models.FloatField(null=False)
    loss_of_pay = models.FloatField(null=False)

    def save(self, *args, **kwargs):
        """Automatically calculate present_days before saving."""
        self.present_days = self.total_days_of_month - (self.holidays + self.week_offs + self.loss_of_pay)
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.employee.name} - {self.month}/{self.financial_year}: Present {self.present_days},"
                f" Casual Leaves {self.casual_leaves}, Sick Leaves {self.sick_leaves}, "
                f"Earned Leaves {self.earned_leaves}")


@receiver(pre_save, sender=EmployeeAttendance)
def update_leave_balance(sender, instance, **kwargs):
    """Validate and update Employee Leave Balance before saving attendance."""

    if instance.pk:  # Only validate updates, not new records
        previous = EmployeeAttendance.objects.get(pk=instance.pk)

        # Define all leave types including Loss of Pay
        leave_types = {
            'casual_leaves': 'Casual Leaves',
            'sick_leaves': 'Sick Leaves',
            'earned_leaves': 'Earned Leaves',
            'loss_of_pay': 'Loss of Pay'
        }

        for field, leave_name in leave_types.items():
            prev_value = getattr(previous, field)
            new_value = getattr(instance, field)
            leave_diff = new_value - prev_value  # Change in leave usage

            if leave_diff != 0:  # Only process if there is a change
                leave_balance = EmployeeLeaveBalance.objects.filter(
                    employee=instance.employee,
                    leave_type__name_of_leave=leave_name,
                    financial_year=instance.financial_year  # Ensure financial year is considered
                ).first()

                if not leave_balance:
                    leave_policies = LeaveManagement.objects.filter(payroll=instance.employee.payroll)

                    start_year, end_year = instance.financial_year.split('-')

                    leave_period_start = date(int(start_year), 4, 1)
                    leave_period_end = date(int(end_year), 3, 31)

                    for leave in leave_policies:
                        total_leaves = leave.number_of_leaves
                        print(total_leaves)
                        pro_rated_leave = total_leaves  # Default full allocation

                        # Calculate remaining months in the financial year
                        if instance.employee.doj > leave_period_start:
                            remaining_months = max(1, (leave_period_end.year - instance.employee.doj.year) * 12 +
                                                   (leave_period_end.month - instance.employee.doj.month))

                            if leave.employee_leave_period == "Monthly":
                                # If leave is allocated monthly, multiply remaining months by number_of_leaves
                                pro_rated_leave = total_leaves * remaining_months

                            elif leave.employee_leave_period == "Annually":
                                # If leave is allocated annually, divide annual leave by remaining months
                                pro_rated_leave = abs(round((total_leaves / 12) * remaining_months))

                        # Create Leave Balance Entry
                        EmployeeLeaveBalance.objects.create(
                            employee=instance.employee,
                            leave_type=leave,
                            leave_entitled=pro_rated_leave,
                            leave_remaining=pro_rated_leave,
                            financial_year=f"{start_year}-{end_year}"
                        )

                else:
                    # If the leave type is NOT LOP, enforce balance limits
                    if leave_name != "Loss of Pay" and leave_diff > 0:
                        if leave_balance.leave_remaining < leave_diff:
                            raise ValidationError(f"Insufficient {leave_name}. You have only {leave_balance.leave_remaining} left.")

                        # Deduct leave from balance
                        leave_balance.leave_remaining = leave_balance.leave_remaining - leave_diff

                    # Update leave used count
                    leave_balance.leave_used += leave_diff
                    leave_balance.save()


class EmployeeSalaryHistory(models.Model):
    employee = models.ForeignKey(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_salary_history'
    )
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='payroll_employee_dashboard')
    month = models.IntegerField(null=False)  # Month of the change
    financial_year = models.CharField(max_length=10, null=False, blank=False)  # Format: "2024-2025"
    total_days_of_month = models.IntegerField(null=False)  # Total days in the month
    lop = models.FloatField(null=False)  # Loss of Pay
    paid_days = models.FloatField(null=False)  # Paid days
    ctc = models.IntegerField(null=False)  # Total CTC
    gross_salary = models.IntegerField(null=False)  # Gross Salary
    earned_salary = models.IntegerField(null=False)  # Earned Salary
    basic_salary = models.FloatField(null=False)  # Basic Salary
    hra = models.FloatField(null=False)  # House Rent Allowance
    conveyance_allowance = models.FloatField(null=False, default=0)  # Conveyance Allowance
    travelling_allowance = models.FloatField(null=False, default=0)  # Travelling Allowance
    commission = models.FloatField(null=False, default=0)  # Commission
    children_education_allowance = models.FloatField(null=False, default=0)  # Children Education Allowance
    overtime_allowance = models.FloatField(null=False, default=0)  #OverTime  Allowance
    transport_allowance = models.FloatField(null=False, default=0)  # Transport Allowance
    special_allowance = models.FloatField(null=False)  # Special Allowance
    bonus = models.FloatField(null=False)  # Bonus
    other_earnings = models.FloatField(null=False)  # Fixed Allowance or other earnings
    benefits_total = models.IntegerField(null=False)  # Total Benefits
    epf = models.FloatField(null=False)  # EPF Contribution
    esi = models.FloatField(null=False)  # ESI Contribution
    pt = models.FloatField(null=False)  # Professional Tax

    monthly_fixed_tds = models.FloatField(null=True)  # Monthly Fixed TDS
    tds = models.FloatField(null=False)  # Tax Deducted at Source
    tds_ytd = models.FloatField(null=False)  # cummulative tds
    
    annual_tds=models.FloatField(null=False) # Yearly Tds
    bonus_incentive = models.FloatField(null=True)  # Bonus or Incentive
    loan_emi = models.FloatField(null=False)  # Loan EMI
    other_deductions = models.FloatField(null=False)  # Other Deductions
    total_deductions = models.FloatField(null=False)  # Total Deductions
    net_salary = models.IntegerField(null=False)  # Net Salary
    is_active = models.BooleanField(default=True)  # Whether the record is active
    change_date = models.DateField(auto_now_add=True)  # Date of the change
    notes = models.TextField(null=True, blank=True)  # Optional notes about the change
    other_earnings_breakdown = models.JSONField(
        default=list,
        blank=True,
        help_text="List of dictionaries with 'component_name' and 'amount'"
    )
    other_deductions_breakdown = models.JSONField(
        default=list,
        blank=True,
        help_text="List of {'component_name': 'Name', 'amount': 500}"
    )

    def __str__(self):
        return f"{self.employee.associate_id} - {self.change_date}"


class PayrollWorkflow(models.Model):
    STATUS_CHOICES = [
        ('in progress', 'in progress'),
        ('completed', 'completed'),
        ('approved', 'approved'),
    ]

    payroll = models.ForeignKey(
        'PayrollOrg',
        on_delete=models.CASCADE,
        related_name='payroll_workflow'
    )

    month = models.IntegerField(null=False)  # Month (1–12)
    financial_year = models.CharField(max_length=10, null=False, blank=False)  # Format: "2024-2025"

    new_joinees = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    exits = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    attendance = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    bonuses = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    adhoc_bonuses = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    salary_revision = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    tds = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    loans_and_advances = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    lock_payroll = models.BooleanField(default=False)
    finalize = models.BooleanField(default=False)  # Whether payroll is finalized
    created_on = models.DateField(auto_now_add=True)  # Automatically set when created

    def __str__(self):
        return f"Payroll Workflow for {self.payroll.name} - {self.month}/{self.financial_year}"


class EmployeeCredentials(models.Model):
    employee = models.OneToOneField(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_credentials'
    )
    username = models.CharField(max_length=150, unique=True)  # Unique username for the employee
    password = models.CharField(max_length=128)  # Password field (hashed)
    last_login = models.DateTimeField(null=True, blank=True)  # Last login timestamp

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.employee.associate_id} - {self.username}"

    @property
    def is_authenticated(self):
        """Allows DRF to treat this object as an authenticated user"""
        return True


class EmployeeEducationDetails(models.Model):
    employee = models.ForeignKey('EmployeeCredentials', on_delete=models.CASCADE, related_name='education_details')
    qualification = models.CharField(max_length=120, null=False, blank=False)
    year_of_passing = models.IntegerField(null=False, blank=False)
    upload_certificate = models.FileField(upload_to=employee_education_certificate, null=True, blank=True)

    def __str__(self):
        return f"{self.employee.employee.associate_id} - {self.qualification} ({self.year_of_passing})"


class AttendanceLog(models.Model):
    CHECKIN_TYPES = [
        ('manual', 'Manual'),
        ('geo', 'Geo Location'),
        ('face', 'Face Recognition'),
        ('qr', 'QR Code'),
        ('timesheet', 'Timesheet'),
        ('biometric', 'Biometric Device'),
        ('auto', 'System Auto'),
    ]
    employee = models.ForeignKey(EmployeeCredentials, on_delete=models.CASCADE, related_name='attendance_logs')
    date = models.DateField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    check_in_type = models.CharField(max_length=20, choices=CHECKIN_TYPES)
    location = models.CharField(max_length=255, blank=True)
    device_info = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.associate_id} - {self.date} ({self.check_in_type})"


class AttendanceGeoTag(models.Model):
    payroll = models.ForeignKey(
        PayrollOrg,
        on_delete=models.CASCADE,
        related_name='geo_locations'  # Consider plural for reverse relation
    )
    branch = models.OneToOneField(WorkLocations, on_delete=models.CASCADE, related_name='branch_location')
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    radius = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"GeoLocation for {self.payroll} at ({self.latitude}, {self.longitude}) with radius {self.radius}"


class EmployeeFaceRecognition(models.Model):
    DIRECTION_CHOICES = [
        ('front', 'Front Face'),
        ('left', 'Left Profile'),
        ('right', 'Right Profile'),
        ('upper_angle', 'Upper Angle'),
        ('lower_angle', 'Lower Angle'),
        ('back', 'back')
    ]

    employee = models.ForeignKey(EmployeeCredentials, on_delete=models.CASCADE, related_name='images')
    direction = models.CharField(max_length=50, choices=DIRECTION_CHOICES)
    image_file = models.FileField(upload_to=employee_image_upload_path)
    labels = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.direction}"


class LeaveApplication(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('CL', 'Casual Leave'),
        ('SL', 'Sick Leave'),
        ('EL', 'Earned Leave'),
        ('LOP', 'Loss of Pay'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(EmployeeCredentials, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveManagement, on_delete=models.CASCADE, related_name='payroll_leave_applications')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    contact_details = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey(
        EmployeeCredentials,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves'
    )
    cc_to = models.ManyToManyField(
        EmployeeCredentials,
        blank=True,
        related_name='cc_leaves'
    )
    reviewed_on = models.DateTimeField(null=True, blank=True)
    reviewer_comment = models.TextField(blank=True)
    attach_file = models.FileField(upload_to=leave_attachments, null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} - {self.start_date} to {self.end_date}"


def current_financial_year():
    today = date.today()
    if today.month < 4:
        return f"{today.year-1}-{today.year}"
    return f"{today.year}-{today.year+1}"


@receiver(post_save, sender=LeaveApplication)
def update_leave_balance_on_approval(sender, instance, created, **kwargs):
    if instance.status == 'approved':
        leave_days = (instance.end_date - instance.start_date).days + 1

        try:
            leave_balance = EmployeeLeaveBalance.objects.get(
                employee=instance.employee.employee,
                leave_type=instance.leave_type,
                financial_year=current_financial_year()
            )
        except EmployeeLeaveBalance.DoesNotExist:
            return

        if leave_balance.leave_remaining >= leave_days:
            leave_balance.leave_used += leave_days
            leave_balance.save()
        else:
            # Optionally handle rejection due to insufficient balance
            pass

        # Prevent recursive signal call by using update() instead of save()
        LeaveApplication.objects.filter(id=instance.id).update(reviewed_on=now().date())








































