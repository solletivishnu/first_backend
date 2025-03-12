from rest_framework import serializers
from .models import (PayrollOrg, WorkLocations, Departments, SalaryTemplate, PaySchedule,
                     Designation, EPF, ESI, PT, Earnings, Benefits, Deduction, Reimbursement,
                     HolidayManagement, LeaveManagement)
from .models import *


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
    class Meta:
        model = WorkLocations
        fields = '__all__'

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
    class Meta:
        model = Departments
        fields = '__all__'

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
    class Meta:
        model = Designation
        fields = ['id', 'payroll', 'designation_name']

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
                  'include_employer_contribution_in_ctc']

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
        if selected_days < 2:
            raise serializers.ValidationError("At least two days must be selected.")
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


class EmployeeSalaryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalaryDetails
        fields = '__all__'


class EmployeePersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePersonalDetails
        fields = '__all__'


class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankDetails
        fields = '__all__'
