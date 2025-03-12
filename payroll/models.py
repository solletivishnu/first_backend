from django.db import models
from django.core.exceptions import ValidationError
from djongo.models import ArrayField, EmbeddedField, JSONField
from user_management.models import *
from datetime import date
from collections import OrderedDict
from django.db.models.signals import pre_save, post_save


def validate_pincode(value):
    if len(str(value)) != 6:  # Assuming 6-digit pin codes
        raise ValidationError(f"{value} is not a valid pin code.")


class PayrollOrg(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Use auto_now_add for creation timestamp
    logo = models.CharField(max_length=200, null=True, blank=True)
    sender_email = models.EmailField(max_length=120, null=True, blank=True)
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
        return f"{self.dept_name} ({self.dept_code})"


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
    epf_number = models.CharField(max_length=100)  # Adjust max_length as needed
    employee_contribution_rate = models.CharField(max_length=240, null=False, blank=False)
    employer_contribution_rate = models.CharField(max_length=240, null=False, blank=False)
    employer_edil_contribution_in_ctc = models.BooleanField()  # EDLI contribution included
    # in CTC Employees' Deposit Linked Insurance
    include_employer_contribution_in_ctc = models.BooleanField()
    admin_charge_in_ctc = models.BooleanField()  # Admin charge included in CTC
    allow_employee_level_override = models.BooleanField()  # Can employee override PF?
    prorate_restricted_pf_wage = models.BooleanField()  # Prorate restricted PF wage?
    apply_components_if_wage_below_15k = models.BooleanField()
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return f"EPF Details for Payroll: {self.payroll.business.nameOfBusiness} (EPF No: {self.epf_number})"


class ESI(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='esi_details')
    esi_number = models.CharField(max_length=100)  # Adjust max_length as needed
    employee_contribution = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 0.75
    employer_contribution = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 3.25
    include_employer_contribution_in_ctc = models.BooleanField()  # Include employer contribution in CTC?

    def __str__(self):
        return f"ESI Details for Payroll: {self.payroll.business.nameOfBusiness} (ESI No: {self.esi_number})"


class PT(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='pt_details')
    work_location = models.ForeignKey('WorkLocations', on_delete=models.CASCADE, related_name='pt_records')
    pt_number = models.CharField(max_length=100, null=True, blank=True)  # Can be null by default
    slab = JSONField(default=list, blank=True)  # Stores PT slab dynamically
    deduction_cycle = models.CharField(max_length=20, default="Monthly")

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
    deduction_type = models.CharField(max_length=150)  # Type of deduction (e.g., tax, insurance)
    payslip_name = models.CharField(max_length=60, unique=True)  # Display name in the payslip (unique)
    is_active = models.BooleanField(default=True)  # Whether the deduction is active
    frequency = models.CharField(max_length=120)  # Frequency of deduction (e.g., monthly, yearly)

    def __str__(self):
        return f"{self.deduction_type} ({self.payslip_name})"


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
        if selected_days < 2:
            raise ValidationError("At least two days must be selected for the pay schedule.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class LeaveManagement(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='leave_managements')
    name_of_leave = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)  # Ensuring code uniqueness
    leave_type = models.CharField(max_length=60)  # Renamed from `type` to `leave_type`
    employee_leave_period = models.CharField(max_length=80)
    number_of_leaves = models.IntegerField(default=0)
    pro_rate_leave_balance_of_new_joinees_based_on_doj = models.BooleanField(default=False)
    reset_leave_balance = models.BooleanField(default=False)
    reset_leave_balance_type = models.CharField(max_length=20)
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
    applicable_for = models.CharField(max_length=60)

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
    employee_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee_id} ({self.gender})"


class EmployeeSalaryDetails(models.Model):
    employee = models.ForeignKey(
        'EmployeeManagement', on_delete=models.CASCADE, related_name='employee_salary'
    )  # Allows multiple salary records per employee

    annual_ctc = models.IntegerField()

    earnings = models.JSONField(default=list, blank=True)
    gross_salary = models.JSONField(default=dict, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    total_ctc = models.JSONField(default=dict, blank=True)
    deductions = models.JSONField(default=list, blank=True)
    net_salary = models.JSONField(default=dict, blank=True)

    valid_from = models.DateField(auto_now_add=True)  # Salary start date
    valid_to = models.DateField(null=True, blank=True)  # Salary end date (null = current salary)

    def clean(self):
        """Ensure no open salary record exists before adding a new one."""
        active_salary = EmployeeSalaryDetails.objects.filter(employee=self.employee, valid_to__isnull=True).exclude(
            id=self.id).first()

        if active_salary:
            raise ValidationError(
                "An active salary record already exists. Please close the existing record before adding a new one.")

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

    def save(self, *args, **kwargs):
        """Ensure the previous salary is closed before adding a new record."""
        # Close the existing active salary before saving the new one
        active_salary = EmployeeSalaryDetails.objects.filter(employee=self.employee, valid_to__isnull=True).exclude(
            id=self.id).first()

        if active_salary:
            active_salary.valid_to = date.today()
            active_salary.save()

        self.clean()  # Validate the model before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.associate_id} - {self.valid_from}"


class EmployeePersonalDetails(BaseModel):
    MARITAL_CHOICES = [
        ('single', 'single'),
        ('married', 'married'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A Positive (A+)'),
        ('A-', 'A Negative (A-)'),
        ('B+', 'B Positive (B+)'),
        ('B-', 'B Negative (B-)'),
        ('AB+', 'AB Positive (AB+)'),
        ('AB-', 'AB Negative (AB-)'),
        ('O+', 'O Positive (O+)'),
        ('O-', 'O Negative (O-)'),
    ]

    employee = models.ForeignKey('EmployeeManagement', on_delete=models.CASCADE,
                                 related_name='employee_personal_details')
    dob = models.DateField()
    age = models.IntegerField()
    guardian_name = models.CharField(max_length=120, null=False, blank=False)
    pan = models.CharField(max_length=20, null=True, blank=False, default=None)
    aadhar = models.CharField(max_length=80, null=True, blank=False, default=None)
    address = models.JSONField()
    alternate_contact_number = models.CharField(max_length=40, null=True, blank=True, default=None)
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, default='single')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, default='O+')

    def __str__(self):
        return f"{self.employee.associate_id} ({self.dob})"


class EmployeeBankDetails(BaseModel):
    employee = models.ForeignKey('EmployeeManagement', on_delete=models.CASCADE, related_name='employee_bank_details')
    account_holder_name = models.CharField(max_length=150, null=False, blank=False)
    bank_name = models.CharField(max_length=150, null=False, blank=False)
    account_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    ifsc_code = models.CharField(max_length=20, null=False, blank=False)
    branch_name = models.CharField(max_length=150, null=True, blank=True)
    upi_id = models.CharField(max_length=50, null=True, blank=True, default=None)  # Default is None
    is_active = models.BooleanField(default=True)  # To mark active/inactive bank details

    def __str__(self):
        return f"{self.employee.associate_id} - {self.bank_name} ({self.account_number})"































