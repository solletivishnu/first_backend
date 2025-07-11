from rest_framework import serializers
from .models import *
from datetime import date, datetime
from calendar import monthrange
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Sum


class PayrollOrgSerializer(serializers.ModelSerializer):

    class Meta:
        model = PayrollOrg
        fields = '__all__'  # Include all fields from PayrollOrg model

    def create(self, validated_data):
        """
        Create and return a new `PayrollOrg` instance, given the validated data.
        """
        # Create a new PayrollOrg instance using the validated data
        instance = self.Meta.model(**validated_data)
        instance.save()  # Save the instance to the database
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `PayrollOrg` instance, given the validated data.
        """
        # Update the instance attributes with the validated data
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()  # Save the updated instance to the database
        return instance


class WorkLocationSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WorkLocations
        fields = '__all__'

    def get_employee_count(self, obj):
        payroll_id = self.context.get('payroll_id')
        if payroll_id:
            return obj.employee_work_location.filter(payroll_id=payroll_id).count()
        return obj.employee_work_location.count()

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = WorkLocations(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DepartmentsSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Departments
        fields = '__all__'

    def get_employee_count(self, obj):
        payroll_id = self.context.get('payroll_id')
        if payroll_id:
            return obj.employee_department.filter(payroll_id=payroll_id).count()
        return obj.employee_department.count()

    def create(self, validated_data):
        """
        Create and return a new `Department` instance, given the validated data.
        """
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Department` instance, given the validated data.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class DesignationSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Designation
        fields = ['id', 'payroll', 'designation_name', 'employee_count']

    def get_employee_count(self, obj):
        payroll_id = self.context.get('payroll_id')
        if payroll_id:
            return obj.employee_designation.filter(payroll_id=payroll_id).count()
        return obj.employee_designation.count()

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = Designation(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EPFSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPF
        fields = ['id', 'payroll', 'epf_number', 'employee_contribution_rate', 'employer_contribution_rate',
                  'employer_edil_contribution_in_ctc', 'include_employer_contribution_in_ctc',
                  'admin_charge_in_ctc', 'allow_employee_level_override', 'prorate_restricted_pf_wage',
                  'apply_components_if_wage_below_15k', 'is_disabled']

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = EPF(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ESISerializer(serializers.ModelSerializer):
    class Meta:
        model = ESI
        fields = ['id', 'payroll', 'esi_number', 'employee_contribution', 'employer_contribution',
                  'include_employer_contribution_in_ctc', 'is_disabled']

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = ESI(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PTSerializer(serializers.ModelSerializer):
    slab = serializers.JSONField(default=list)

    class Meta:
        model = PT
        fields = ['id', 'payroll', 'work_location', 'pt_number', 'slab', 'deduction_cycle']

    def create(self, validated_data):
        """
        Create and return a new `PF` instance, given the validated data.
        """
        instance = PT.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `PF` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PTSerializerRetrieval(serializers.ModelSerializer):
    work_location_name = serializers.CharField(source='work_location.location_name', read_only=True)
    state = serializers.CharField(source='work_location.address_state', read_only=True)
    slab = serializers.ListField(
        child=serializers.DictField(),  # Each element inside the list is a dictionary (object)
        allow_empty=True  # Allow the list to be empty, if necessary
    )

    class Meta:
        model = PT
        fields = ['id', 'payroll', 'work_location', 'work_location_name', 'state', 'pt_number', 'slab']


class EarningsSerializer(serializers.ModelSerializer):
    calculation_type = serializers.JSONField(default=dict)

    class Meta:
        model = Earnings
        fields = [
            'id', 'payroll', 'component_name', 'component_type', 'is_active', 'calculation_type',
            'is_part_of_employee_salary_structure', 'is_taxable', 'is_pro_rate_basis',
            'is_fbp_component', 'includes_epf_contribution', 'includes_esi_contribution',
            'is_included_in_payslip', 'tax_deduction_preference', 'is_scheduled_earning', 'pf_wage_less_than_15k',
            'always_consider_epf_inclusion'

        ]

    def create(self, validated_data):
        """
        Create and return a new `Earnings` instance, given the validated data.
        """
        instance = Earnings.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Earnings` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EarningsSerializerRetrieval(serializers.ModelSerializer):
    calculation = serializers.SerializerMethodField()
    consider_for_epf = serializers.SerializerMethodField()
    consider_for_esi = serializers.SerializerMethodField()

    class Meta:
        model = Earnings
        fields = [
            'id', 'component_name', 'calculation', 'consider_for_epf',
            'consider_for_esi', 'is_active'
        ]

    def get_calculation(self, obj):
        """Format the calculation field based on calculation_type"""
        calc_type = obj.calculation_type.get("type", "")
        value = obj.calculation_type.get("value", "")

        if calc_type == "Percentage of CTC":
            return f"{value}% of CTC"
        elif calc_type == "Percentage of Basic":
            return f"{value}% of Basic"
        elif calc_type == "Flat Amount":
            return "Flat Amount"
        elif value and calc_type:
            return f"{value} ({calc_type})"
        elif calc_type:
            return calc_type
        else:
            return "Unknown"

    def get_consider_for_epf(self, obj):
        """Return 'True' if EPF is included, otherwise conditionally 'True(pf wage < 16k)'"""
        if obj.includes_epf_contribution:
            return "Yes(pf wage < 15k)" if obj.pf_wage_less_than_15k else "Yes"
        return "No"

    def get_consider_for_esi(self, obj):
        """Return 'Yes' if includes_esi_contribution is True, otherwise 'No'"""
        return "Yes" if obj.includes_esi_contribution else "No"


class BenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits
        fields = [
            'id',
            'payroll',
            'benefit_type',
            'associated_with',
            'payslip_name',
            'is_active',
            'is_pro_rated',
            'includes_employer_contribution',
            'frequency'
        ]

    # Adding validation for unique `payslip_name`
    def validate_payslip_name(self, value):
        if Benefits.objects.filter(payslip_name=value).exists():
            raise serializers.ValidationError("Payslip name must be unique.")
        return value


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = [
            'id',
            'payroll',
            'deduction_type',
            'payslip_name',
            'is_active',
            'frequency'
        ]

    def validate_payslip_name(self, value):
        if Deduction.objects.filter(payslip_name=value).exists():
            raise serializers.ValidationError("Payslip name must be unique.")
        return value


class ReimbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reimbursement
        fields = [
            'id',
            'payroll',
            'reimbursement_type',
            'payslip_name',
            'include_in_flexible_benefit_plan',
            'unclaimed_reimbursement',
            'amount_value',
            'is_active'
        ]

    def validate_payslip_name(self, value):
        if Reimbursement.objects.filter(payslip_name=value).exists():
            raise serializers.ValidationError("Payslip name must be unique.")
        return value

    def validate_amount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Reimbursement amount must be greater than zero.")
        return value


class SalaryTemplateSerializer(serializers.ModelSerializer):
    earnings = serializers.JSONField(default=list)
    gross_salary = serializers.JSONField(default=list)
    benefits = serializers.JSONField(default=list)
    total_ctc = serializers.JSONField(default=list)
    deductions = serializers.JSONField(default=list)
    net_salary = serializers.JSONField(default=list)

    class Meta:
        model = SalaryTemplate
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Earnings` instance, given the validated data.
        """
        instance = SalaryTemplate.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Earnings` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaySchedule
        fields = '__all__'

    def validate(self, data):
        """ Custom validation to ensure at least two days are selected """
        selected_days = sum([
            data.get('sunday', False), data.get('monday', False), data.get('tuesday', False),
            data.get('wednesday', False), data.get('thursday', False), data.get('friday', False),
            data.get('saturday', False), data.get('second_saturday', False), data.get('fourth_saturday', False)
        ])
        return data

    def create(self, validated_data):
        """
        Create and return a new `Earnings` instance, given the validated data.
        """
        instance = PaySchedule.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """Ensure that update returns the instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LeaveManagementSerializer(serializers.ModelSerializer):
    reset_leave_balance_type = serializers.CharField(allow_blank=True, allow_null=True)
    max_carry_forward_days = serializers.CharField(allow_blank=True, allow_null=True)
    encashment_days = serializers.CharField(allow_blank=True, allow_null=True)
    class Meta:
        model = LeaveManagement
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Earnings` instance, given the validated data.
        """
        instance = LeaveManagement.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Earnings` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class HolidayManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayManagement
        fields = '__all__'
        
    def create(self, validated_data):
        """
        Create and return a new `Earnings` instance, given the validated data.
        """
        instance = HolidayManagement.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Earnings` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployeeManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeManagement
        fields = '__all__'

    def validate_unique_fields(self, validated_data, instance=None):
        payroll_id = validated_data.get('payroll')
        work_email = validated_data.get('work_email')
        mobile_number = validated_data.get('mobile_number')
        associate_id = validated_data.get('associate_id')
        uan = validated_data.get('statutory_components', {}).get('employee_provident_fund', {}).get('uan')

        # Build base queryset excluding the current instance (if update)
        qs = EmployeeManagement.objects.filter(payroll_id=payroll_id)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        # Check conflicts
        existing = qs.filter(
            Q(work_email=work_email) |
            Q(mobile_number=mobile_number) |
            Q(associate_id=associate_id)
        ).first()

        if existing:
            if existing.work_email == work_email:
                raise ValidationError("A record with this Work Email already exists.")
            if existing.mobile_number == mobile_number:
                raise ValidationError("A record with this Mobile Number already exists.")
            if existing.associate_id == associate_id:
                raise ValidationError("A record with this Employee ID already exists.")

        if uan and qs.filter(statutory_components__employee_provident_fund__uan=uan).exists():
            raise ValidationError("A record with this UAN already exists.")

    def create(self, validated_data):
        self.validate_unique_fields(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.validate_unique_fields(validated_data, instance=instance)
        return super().update(instance, validated_data)


class EmployeeSalaryDetailsSerializer(serializers.ModelSerializer):
    payroll_month = serializers.IntegerField(write_only=True, required=False)
    payroll_year = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = EmployeeSalaryDetails
        fields = '__all__'

    def create(self, validated_data):
        # Remove non-model fields before creating the instance
        validated_data.pop('payroll_month', None)
        validated_data.pop('payroll_year', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        payroll_month = validated_data.pop('payroll_month', None)
        payroll_year = validated_data.pop('payroll_year', None)

        if payroll_month is not None:
            instance.payroll_month = payroll_month
        if payroll_year is not None:
            instance.payroll_year = payroll_year

        return super().update(instance, validated_data)


class EmployeeSalaryRevisionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalaryRevisionHistory
        fields = '__all__'


class SimplifiedEmployeeSalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    employee_id = serializers.IntegerField(source='employee.id')
    associate_id = serializers.CharField(source='employee.associate_id')
    revision_date = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalaryRevisionHistory
        fields = [
            'id',
            'employee_id',
            'associate_id',  # Include associate_id in response
            'employee_name',
            'department',
            'designation',
            'previous_ctc',
            'current_ctc',
            'revision_date',
        ]

    def get_employee_name(self, obj):
        # Handle potential None values for middle name
        middle_name = f" {obj.employee.middle_name}" if obj.employee.middle_name else ""
        return f"{obj.employee.first_name}{middle_name} {obj.employee.last_name}"

    def get_department(self, obj):
        return obj.employee.department.dept_name if obj.employee.department else None

    def get_designation(self, obj):
        return obj.employee.designation.designation_name if obj.employee.designation else None

    def get_revision_date(self, obj):
        if obj.revision_date:
            return obj.revision_date.strftime('%d-%m-%Y')
        return None



class EmployeePersonalDetailsSerializer(serializers.ModelSerializer):
    payroll = serializers.IntegerField(write_only=True)  # Incoming payroll ID from frontend

    class Meta:
        model = EmployeePersonalDetails
        fields = '__all__'

    def validate_unique_identifiers(self, validated_data, instance=None):
        """
        Shared validator for PAN and Aadhar based on payroll match.
        If `instance` is provided, it's an update operation.
        """
        payroll_id = validated_data.pop('payroll', None)
        employee = validated_data.get('employee') or (instance.employee if instance else None)

        if not employee:
            raise ValidationError("Employee is required.")

        if not hasattr(employee, 'payroll') or employee.payroll.id != payroll_id:
            # Skip PAN/Aadhar validation if payroll doesn't match
            return validated_data

        # PAN validation (skip current instance if updating)
        pan = validated_data.get('pan')
        if pan:
            qs = EmployeePersonalDetails.objects.filter(pan=pan)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise ValidationError("A record with this PAN already exists.")

        # Aadhar validation (skip current instance if updating)
        aadhar = validated_data.get('aadhar')
        if aadhar:
            qs = EmployeePersonalDetails.objects.filter(aadhar=aadhar)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise ValidationError("A record with this Aadhar already exists.")

        return validated_data

    def create(self, validated_data):
        validated_data = self.validate_unique_identifiers(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.validate_unique_identifiers(validated_data, instance)
        return super().update(instance, validated_data)


class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankDetails
        fields = '__all__'


class EmployeeDataSerializer(serializers.ModelSerializer):
    employee_salary = EmployeeSalaryDetailsSerializer(read_only=True)
    employee_personal_details = EmployeePersonalDetailsSerializer(read_only=True)
    employee_bank_details = EmployeeBankDetailsSerializer(read_only=True)

    designation_name = serializers.CharField(source='designation.designation_name', read_only=True)
    department_name = serializers.CharField(source='department.dept_name', read_only=True)

    class Meta:
        model = EmployeeManagement
        fields = '__all__'


class CurrentMonthEmployeeDataSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    total_days_in_month = serializers.SerializerMethodField()
    paid_days = serializers.SerializerMethodField()
    gross_salary = serializers.SerializerMethodField()
    annual_ctc = serializers.SerializerMethodField()
    designation_name = serializers.CharField(source='designation.designation_name', read_only=True)
    department_name = serializers.CharField(source='department.dept_name', read_only=True)

    class Meta:
        model = EmployeeManagement
        fields = [
            "id",
            "employee_name",
            "department_name",
            "designation_name",
            "associate_id",
            "doj",
            "total_days_in_month",
            "paid_days",
            "gross_salary",
            "annual_ctc",
        ]

    def get_employee_name(self, obj):
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}".strip()

    def get_total_days_in_month(self, obj):
        """Returns the total days in the month of DOJ (Joining Date)."""
        doj_date = obj.doj
        _, days_in_month = monthrange(doj_date.year, doj_date.month)
        return days_in_month

    def get_paid_days(self, obj):
        """Calculates paid days = Total Days - Holidays - Off Days from PaySchedule"""
        doj_date = obj.doj
        year, month = doj_date.year, doj_date.month
        _, days_in_month = monthrange(year, month)

        # 🔹 Step 1: Get PaySchedule for the Payroll
        pay_schedule = PaySchedule.objects.filter(payroll=obj.payroll).first()

        # Get first and last day of the month
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, days_in_month).date()

        # Fetch all holidays in that month
        holidays = HolidayManagement.objects.filter(
            payroll=obj.payroll,
            start_date__gte=first_day,
            start_date__lte=last_day
        ).values_list('start_date', flat=True)

        # 🔹 Step 3: Determine Off Days (Saturdays, Sundays, etc.)
        off_days = set()
        for day in range(1, days_in_month + 1):
            date = doj_date.replace(day=day)
            weekday = date.weekday()  # 0 = Monday, 6 = Sunday

            if pay_schedule:
                if (weekday == 0 and pay_schedule.monday) or \
                   (weekday == 1 and pay_schedule.tuesday) or \
                   (weekday == 2 and pay_schedule.wednesday) or \
                   (weekday == 3 and pay_schedule.thursday) or \
                   (weekday == 4 and pay_schedule.friday) or \
                   (weekday == 5 and pay_schedule.saturday) or \
                   (weekday == 6 and pay_schedule.sunday):
                    off_days.add(date)

                # Handle Second & Fourth Saturday
                if pay_schedule.second_saturday and (day >= 8 and day <= 14 and weekday == 5):
                    off_days.add(date)
                if pay_schedule.fourth_saturday and (day >= 22 and day <= 28 and weekday == 5):
                    off_days.add(date)

        # 🔹 Step 4: Calculate Paid Days
        paid_days = days_in_month - len(holidays) - len(off_days)

        return max(0, paid_days)  # Ensure it doesn't go negative

    def get_gross_salary(self, obj):
        """Retrieves the gross monthly salary of the employee if available."""
        salary = getattr(obj, 'employee_salary', None)

        return round(salary.gross_salary.get('monthly', 0), 2) if salary and salary.gross_salary else 0

    def get_annual_ctc(self, obj):
        """Retrieves the annual CTC of the employee if available."""
        salary = getattr(obj, 'employee_salary', None)

        return salary.annual_ctc if salary and salary.annual_ctc else 0


class PayrollEPFESISerializer(serializers.ModelSerializer):
    epf_details = EPFSerializer(read_only=True)
    esi_details = ESISerializer(read_only=True)
    pt_details = PTSerializer(many=True, read_only=True)

    class Meta:
        model = PayrollOrg
        fields = ['id', 'epf_details', 'esi_details', 'pt_details']


class EmployeeExitSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeExit
        fields = '__all__'

    def get_department(self, obj):
        """Fetch employee's department"""
        return obj.employee.department.dept_name

    def get_designation(self, obj):
        """Fetch employee's designation"""
        return obj.employee.designation.designation_name


class AdvanceLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceLoan
        fields = '__all__'

    def validate(self, data):
        """Ensure no_of_months is valid"""
        if data.get('no_of_months') <= 0:
            raise serializers.ValidationError({"error": "Number of months must be greater than zero."})
        return data


class BonusIncentiveSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    associate_id = serializers.CharField(source='employee.associate_id', read_only=True)

    committed_bonus = serializers.SerializerMethodField()
    ytd = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()

    class Meta:
        model = BonusIncentive
        fields = [
            'id',  # or whatever actual fields your model has
            'employee', 'amount', 'financial_year', 'month', 'bonus_type',
            'employee_name', 'department', 'designation', 'associate_id',
            'committed_bonus', 'ytd', 'remaining_balance', 'remarks'
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.middle_name} {obj.employee.last_name}".strip()

    def get_department(self, obj):
        return obj.employee.department.dept_name

    def get_designation(self, obj):
        return obj.employee.designation.designation_name

    def get_committed_bonus(self, obj):
        """Get committed bonus amount from EmployeeSalaryDetails if variable bonus is enabled"""
        salary = EmployeeSalaryDetails.objects.filter(employee=obj.employee, valid_to__isnull=True).first()
        if salary and salary.is_variable_bonus:
            return salary.variable_bonus.get("bonus_amount", 0)
        return 0

    def get_ytd(self, obj):
        """Get year-to-date total bonus paid to employee for the current financial year"""
        total = BonusIncentive.objects.filter(
            employee=obj.employee,
            financial_year=obj.financial_year
        ).aggregate(total_bonus=Sum('amount'))['total_bonus']
        return total or 0

    def get_remaining_balance(self, obj):
        committed = self.get_committed_bonus(obj)
        ytd = self.get_ytd(obj)
        return committed - ytd


class AdvanceLoanDetailSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()

    class Meta:
        model = AdvanceLoan
        fields = '__all__'

    def get_employee_name(self, obj):
        """Returns the formatted employee name"""
        return f"{obj.employee.first_name} {obj.employee.middle_name} {obj.employee.last_name}".strip()

    def get_department(self, obj):
        """Fetch employee's department"""
        return obj.employee.department.dept_name

    def get_designation(self, obj):
        """Fetch employee's designation"""
        return obj.employee.designation.designation_name


class AdvanceLoanSummarySerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    pending_balance = serializers.SerializerMethodField()
    current_month_deduction = serializers.SerializerMethodField()
    associate_id = serializers.CharField(source='employee.associate_id', read_only=True)

    class Meta:
        model = AdvanceLoan
        fields = [
            "id",
            "employee_name",
            "department",
            "designation",
            "associate_id",
            "loan_type",
            "amount",
            "emi_amount",
            "end_month",
            "pending_balance",
            "current_month_deduction"
        ]

    def get_employee_name(self, obj):
        """Returns the formatted employee name"""
        return f"{obj.employee.first_name} {obj.employee.middle_name} {obj.employee.last_name}".strip()

    def get_department(self, obj):
        """Fetch employee's department"""
        return obj.employee.department.dept_name

    def get_designation(self, obj):
        """Fetch employee's designation"""
        return obj.employee.designation.designation_name

    def get_pending_balance(self, obj):
        """Calculates remaining loan balance"""
        current_date = self.context.get("current_date")
        if not current_date:
            current_date = datetime.now().date()

        months_paid = (current_date.year - obj.start_month.year) * 12 + (current_date.month - obj.start_month.month)
        pending_balance = obj.amount - (months_paid * obj.emi_amount)

        return max(0, pending_balance)  # Ensure no negative balance

    def get_current_month_deduction(self, obj):
        """Returns EMI deduction for the current month"""
        pending_balance = self.get_pending_balance(obj)
        return obj.emi_amount if pending_balance > 0 else 0


class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAttendance
        fields = '__all__'


class EmployeeSalaryHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    regime = serializers.SerializerMethodField()
    pan = serializers.SerializerMethodField()
    associate_id = serializers.CharField(source='employee.associate_id', read_only=True)

    class Meta:
        model = EmployeeSalaryHistory
        fields = '__all__'

    def get_employee_name(self, obj):
        """Returns the formatted employee name"""
        return f"{obj.employee.first_name} {obj.employee.middle_name} {obj.employee.last_name}".strip()

    def get_department(self, obj):
        """Fetch employee's department"""
        return obj.employee.department.dept_name

    def get_designation(self, obj):
        """Fetch employee's designation"""
        return obj.employee.designation.designation_name

    def get_regime(self, obj):
        """Fetch tax regime opted from salary details"""
        try:
            return obj.employee.employee_salary.tax_regime_opted
        except AttributeError:
            return None

    def get_pan(self, obj):
        """Fetch PAN from employee's personal details"""
        try:
            return obj.employee.employee_personal_details.pan
        except AttributeError:
            return None


class EmployeeSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeManagement
        fields = ['id', 'associate_id', 'full_name']

    def get_full_name(self, obj):
        middle = obj.middle_name
        middle_part = f" {middle}" if middle and str(middle).lower() != 'nan' else ''
        return f"{obj.first_name}{middle_part} {obj.last_name}".strip()


class PayrollWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollWorkflow
        fields = '__all__'

