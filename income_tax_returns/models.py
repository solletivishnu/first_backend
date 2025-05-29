from django.db import models
from Tara.settings.default import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from djongo.models import ArrayField, EmbeddedField, JSONField
from .helpers import *
from usermanagement.models import ServiceRequest, Users
from servicetasks.models import ServiceTask
from django.db.models.signals import post_save
from django.dispatch import receiver


class PersonalInformation(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='personal_information')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_personal_information')
    first_name = models.CharField(max_length=255, null=False, blank=False)
    middle_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(max_length=255, null=False, blank=False)
    residentail_status = models.CharField(max_length=255, null=False, blank=False)
    pan = models.FileField(upload_to=personal_information_pan, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=False, blank=False, default=None)
    email = models.EmailField(max_length=255, null=False, blank=False, default=None)
    aadhar = models.FileField(upload_to=personal_information_aadhar, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personal_information_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personal_information_reviewed'
    )
    non_resident_indian = models.CharField(max_length=255, null=True, blank=True)
    salary_income = models.CharField(max_length=5, null=True, blank=True,
                                     choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    other_income = models.CharField(max_length=5, null=True, blank=True,
                                    choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    house_property_income = models.CharField(max_length=5, null=True, blank=True,
                                             choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    capital_gains = models.CharField(max_length=5, null=True, blank=True,
                                       choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    business_income = models.CharField(max_length=5, null=True, blank=True,
                                       choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    agriculture_income = models.CharField(max_length=5, null=True, blank=True,
                                          choices=[('yes', 'Yes'), ('no', 'No')], default='no')


    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name


class TaxPaidDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='tax_paid_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_tax_paid_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_paid_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_paid_details_reviewed'
    )

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Tax Paid Details"


class TaxPaidDetailsFile(models.Model):
    DOCUMENT_TYPES = [
        ('26AS', '26As'),
        ('AIS', 'AIS'),
        ('AdvanceTax', 'AdvanceTax'),
    ]

    tax_paid = models.ForeignKey(TaxPaidDetails, on_delete=models.CASCADE, related_name='tax_paid_documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=tax_paid_details_file,
                           null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tax_paid.service_request.id} - {self.document_type}"


class SalaryIncome(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='salary_income_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_salary_income_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salary_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salary_income_reviewed'
    )
    form_16_notes = models.TextField(null=True, blank=True, default=None)
    payslip_notes = models.TextField(null=True, blank=True, default=None)
    bank_statement_notes = models.TextField(null=True, blank=True, default=None)


    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Tax Paid Details"


class SalaryDocumentFile(models.Model):
    DOCUMENT_TYPES = [
        ('FORM_16', 'Form 16'),
        ('PAYSLIP', 'Payslip'),
        ('BANK_STATEMENT', 'Bank Statement'),
    ]

    income = models.ForeignKey(SalaryIncome, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=salary_income_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.income.service_request.id} - {self.document_type}"


class OtherIncomeDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='other_income_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_other_income_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_details_reviewed'
    )
    details = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField()
    file = models.FileField(upload_to=outcome_income_details_file,
                            null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Foreign Employee Salary Details"


class NRIEmployeeSalaryDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='foreign_income_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE, related_name='service_task_foreign_income_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foreign_income_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foreign_income_details_reviewed'
    )
    foreign_salary_and_employment = models.CharField(max_length=255, null=True, blank=True)
    employment_history = JSONField(null=True, blank=True, default=[])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Foreign Employee Salary Details"


class ForeignEmployeeSalaryDetailsFiles(models.Model):
    DOCUMENT_TYPES = [
        ('SALARY_SLIP', 'Salary Slip'),
        ('TAX_PAID_CERTIFICATE_BOARD', 'TAX PAID CERTIFICATE BOARD'),
        ('BANK_STATEMENT', 'Bank Statement'),
    ]

    nri = models.ForeignKey(NRIEmployeeSalaryDetails, on_delete=models.CASCADE, related_name='foreigner_documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=foreign_emp_salary_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.income.service_request.id} - {self.document_type}"


class HousePropertyIncomeDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='house_property_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_house_property_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='house_property_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='house_property_details_reviewed'
    )
    type_of_property = models.CharField(max_length=255, null=True, blank=True)
    property_address = JSONField(null=True, blank=True, default=dict)
    owned_property = models.BooleanField(default=False)
    ownership_percentage = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    is_it_property_let_out = models.BooleanField(default=False)
    annual_rent_received = models.IntegerField(null=True, blank=True)
    rent_received = models.CharField(max_length=255, null=True, blank=True)
    pay_municipal_tax = models.BooleanField(default=False)
    municipal_tax_paid = models.IntegerField(null=True, blank=True)
    municipal_tax_receipt = models.FileField(upload_to=house_property_details_municipal_tax_receipt, null=True, blank=True)
    home_loan_on_property = models.BooleanField(default=False)
    interest_during_financial_year = models.IntegerField(null=True, blank=True)
    principal_during_financial_year = models.IntegerField(null=True, blank=True)
    loan_statement = models.FileField(upload_to=house_property_details_loan_statement, null=True, blank=True)
    upload_loan_interest_certificate = models.FileField(upload_to=house_property_details_loan_interest_certificate, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - House Property Details"


class CapitalGainsApplicableDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='capital_gains_applicable_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_capital_gains_applicable_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_gains_applicable_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_gains_applicable_details_reviewed'
    )

    gains_applicable = JSONField(null=True, blank=True, default=[])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Capital Gains Applicable Details"


class CapitalGainsProperty(models.Model):
    capital_gains_applicable = models.ForeignKey(CapitalGainsApplicableDetails, on_delete=models.CASCADE,
                                                 related_name='capital_gains_property_details')
    property_type = models.CharField(max_length=120, null=False, blank=False, choices=[('land', 'land'),
                                                                                       ('plot', 'plot'),
                                                                                       ('building', 'building')])
    date_of_purchase = models.DateField()
    purchase_cost = models.IntegerField()
    date_of_sale = models.DateField()
    sale_value = models.IntegerField()
    purchase_doc = models.FileField(upload_to=capital_gains_property_purchase_doc, null=True, blank=True)
    sale_doc = models.FileField(upload_to=capital_gains_property_sale_doc, null=True, blank=True)
    reinvestment_details = JSONField(default=dict, null=True, blank=True)
    reinvestment_details_docs = models.FileField(upload_to=capital_gains_property_reinvestment_docs,
                                                 null=True, blank=True)

    def __str__(self):
        return f"{self.capital_gains_applicable.service_request.id} - {self.property_type} Details"


class CapitalGainsEquityMutualFund(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='capital_gains_equity_mutual_funds')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_capital_gains_equity_mutual_funds')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_gains_equity_mutual_funds_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_gains_equity_mutual_funds_reviewed'
    )
    equity_mutual_fund_type = JSONField(null=True, blank=True, default=list)
    sell_any_foreign_sales = models.CharField(max_length=20, choices=[('yes', 'yes'), ('no', 'no')], default='no')
    sell_any_unlisted_sales = models.CharField(max_length=20, choices=[('yes', 'yes'), ('no', 'no')], default='no')

    def __str__(self):
        return f"{self.service_request.id} - Equity Mutual Fund Details"


class CapitalGainsEquityMutualFundDocument(models.Model):
    capital_gains_equity_mutual_fund = models.ForeignKey(CapitalGainsEquityMutualFund, on_delete=models.CASCADE,
                                                          related_name='documents')
    file = models.FileField(upload_to=capital_gains_equity_mutual_fund_file, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.capital_gains_equity_mutual_fund.service_request.id} - {self.document_type}"


class OtherCapitalGains(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='capital_gains_other_capital_gains')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_capital_gains_other_capital_gains')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_gains_other_capital_gains_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_gains_other_capital_gains_reviewed'
    )
    asset_details = models.CharField(max_length=120, null=False, blank=False)
    purchase_date = models.DateField()
    sale_date = models.DateField()
    sale_value = models.IntegerField()
    purchase_value = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.service_request.id} - Other Capital Gains Details"


class OtherCapitalGainsDocument(models.Model):
    other_capital_gains = models.ForeignKey(OtherCapitalGains, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to=other_capital_gains_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.other_capital_gains.service_request.id} - {self.file.name}"


class BusinessProfessionalIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='business_professional_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE, related_name='service_task_business_professional_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_professional_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_professional_income_reviewed'
    )
    business_name = models.CharField(max_length=255, null=False, blank=False)
    business_type = models.CharField(max_length=255, null=False, blank=False)
    opting_for_presumptive_taxation = models.CharField(max_length=255, null=False, blank=False,
                                                       choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    opting_data = JSONField(default={}, null=True, blank=True)
    gst_registered = models.CharField(max_length=255, null=False, blank=False,
                                      choices=[('yes', 'Yes'), ('no', 'No')], default='no')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Business Professional Income Details"


class BusinessProfessionalIncomeDocument(models.Model):
    business_professional_income = models.ForeignKey(BusinessProfessionalIncome, on_delete=models.CASCADE,
                                                     related_name='documents')
    document_type = models.CharField(max_length=30, choices=[('26AS', '26AS'),
                                                             ('GST Returns', 'GST Returns'),
                                                             ('Bank Statements', 'Bank Statements'),
                                                             ('Other', 'Other'),
                                                             ('AIS', 'AIS')])
    file = models.FileField(upload_to=business_professional_income_file, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_professional_income.service_request.id} - {self.document_type}"


class InterestIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='other_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE, related_name='service_task_other_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_reviewed'
    )
    interest_income = models.CharField(max_length=255, null=False, blank=False,
                                       choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Other Income Details"


class InterestIncomeDocument(models.Model):
    interest_income = models.ForeignKey(InterestIncome, on_delete=models.CASCADE, related_name='documents')
    interest_type = models.CharField(max_length=30, choices=[('Savings Account', 'Savings Account'),
                                                             ('Recurring Deposit', 'Recurring Deposit'),
                                                             ('NRO Account', 'NRO Account'),
                                                             ('NRE Account', 'NRE Account'),
                                                             ('Other', 'Other'),
                                                             ('Fixed Deposit', 'Fixed Deposit')])
    interest_earned = models.IntegerField(null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=interest_income_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interest_income.service_request.id} - {self.document_type}"


class DividendIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='dividend_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE, related_name='service_task_dividend_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dividend_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dividend_income_reviewed'
    )
    dividend_income = models.CharField(max_length=255, null=False, blank=False,
                                       choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Other Income Details"


class DividendIncomeDocument(models.Model):
    dividend_income = models.ForeignKey(DividendIncome, on_delete=models.CASCADE, related_name='documents')
    received_from = models.CharField(max_length=255, null=True, blank=True)
    dividend_received = models.IntegerField(null=True, blank=True)
    file = models.FileField(upload_to=dividend_income_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dividend_income.service_request.id}- {self.received_from}"


class GiftIncomeDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='gift_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_gift_income_details')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gift_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gift_income_reviewed'
    )
    gift_income = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Gift Income Details"


class GiftIncomeDocument(models.Model):
    gift_income = models.ForeignKey(GiftIncomeDetails, on_delete=models.CASCADE, related_name='gift_income_details')
    amount = models.IntegerField(null=True, blank=True)
    received_from = models.CharField(max_length=255, null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True, choices=[('Relative', 'Relative'),
                                                                                ('Non Relative', 'Non Relative')])
    date_received = models.DateField(null=True, blank=True)
    was_it_marriage_related = models.CharField(max_length=255, null=True, blank=True,
                                               choices=[('Yes', 'Yes'), ('No', 'No')])

    def __str__(self):
        return f"{self.gift_income.service_request.id}- {self.relation}"


class FamilyPensionIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='family_pension_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_family_pension_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='family_pension_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='family_pension_reviewed'
    )
    family_pension_income = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Family Pension Income Details"


class FamilyPensionIncomeInfo(models.Model):
    family_pension = models.ForeignKey(FamilyPensionIncome, on_delete=models.CASCADE,
                                       related_name='family_pension_income_docs')
    source = models.CharField(max_length=30, choices=[('Government', 'Government'),
                                                      ('Private', 'Private'),
                                                      ('Others', 'Others')])
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.family_pension.service_request.id}- {self.source}"


class ForeignIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='foreign_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_foreign_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foreign_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foreign_income_reviewed'
    )
    foreign_income = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Family Pension Income Details"


class ForeignIncomeInfo(models.Model):
    foreign_income = models.ForeignKey(ForeignIncome, on_delete=models.CASCADE,
                                       related_name='foreign_income_docs')
    type_of_income = models.CharField(max_length=30, choices=[('Divident', 'Divident'),
                                                              ('Interest', 'Interest'),
                                                              ('Others', 'Others')])
    country = models.CharField(max_length=20)
    currency = models.CharField(max_length=3)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.foreign_income.service_request.id}- {self.type_of_income}"


class WinningIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='winnings')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_winnings_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='winnings_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='winnings_income_reviewed'
    )
    winning_income = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Winning Income Details"


class WinningIncomeDocument(models.Model):
    winning_income = models.ForeignKey(WinningIncome, on_delete=models.CASCADE, related_name='winnings_income_docs')
    source = models.CharField(max_length=30, choices=[('Lottery', 'Lottery'),
                                                      ('Game Show', 'Game Show'),
                                                      ('amount', 'amount')])
    amount = models.IntegerField()
    file = models.FileField(upload_to=winning_income_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.winning_income.service_request.id}- {self.received_from}"


class AgricultureIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='agriculture_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_agriculture_income')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agriculture_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agriculture_incomereviewed'
    )
    agriculture = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Winning Income Details"


class AgricultureIncomeDocument(models.Model):
    agriculture_income = models.ForeignKey(AgricultureIncome, on_delete=models.CASCADE,
                                       related_name='agriculture_income_docs')
    amount = models.IntegerField()
    file = models.FileField(upload_to=agriculture_income_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agriculture_income.service_request.id}- {self.amount}"


class Deductions(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='deductions')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_deductions')
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deductions_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deductions_reviewed'
    )

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Deductions Details"


class Section80G(models.Model):
    deductions = models.ForeignKey(Deductions, on_delete=models.CASCADE, related_name='section_80g')
    name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    mode = models.CharField(max_length=50, null=True, blank=True,choices=[('Cash', 'Cash'),
                                                                          ('Cheque', 'Cheque'),
                                                                          ('Online Transfer', 'Online Transfer')])
    file = models.FileField(upload_to=section_80g_file, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deductions.service_request.id} - Section 80G Donation"


class Section80ETTATTBU(models.Model):
    deductions = models.OneToOneField(Deductions, on_delete=models.CASCADE, related_name='section_80ettattbu')
    amount = models.IntegerField(null=True, blank=True)
    education_of = models.CharField(max_length=50, null=True, blank=True, choices=[('self', 'self'),
                                                                                   ('spouse', 'spouse'),
                                                                                   ('children', 'children'),
                                                                                   ('dependent', 'dependent')])
    borrower_name = models.CharField(max_length=50, null=True, blank=True)
    is_it_approved_bank = models.BooleanField(default=False)
    total_saving_interest = models.IntegerField(null=True, blank=True)
    total_fd_interest = models.IntegerField(null=True, blank=True)
    nature_of_disability = models.CharField(max_length=50, null=True, blank=True,
                                            choices=[('Blindness', 'Blindness'),
                                                     ('Deaf and Dumb', 'Deaf and Dumb'),
                                                     ('Low Vision', 'Low Vision'),
                                                     ('Leprosy Cured', 'Leprosy Cured'),
                                                     ('Hearing Impairment', 'Hearing Impairment'),
                                                     ('Locomotor Disability', 'Locomotor Disability'),
                                                     ('Mental Illness', 'Mental Illness'),
                                                     ('Mental Retardation', 'Mental Retardation'),
                                                     ('Multiple Disabilities', 'Multiple Disabilities'),
                                                     ('others', 'others')]
                                            )
    severity = models.CharField(max_length=50, null=True, blank=True, choices=[('40-80%', '40-80%'),('>80%', '>80%')])
    deduction_amount = models.IntegerField(null=True, blank=True)

    deduction_file = models.FileField(upload_to=section_80ettattbu_file, null=True, blank=True)
    pay_rent_without_recieving_hra = models.BooleanField(default=False)
    pay_rent_amount = models.IntegerField(null=True, blank=True)
    are_you_first_time_homebuyer = models.BooleanField(default=False)
    amount_of_interest_paid = models.IntegerField(null=True, blank=True)
    date_of_loan_sanctioned = models.DateField(null=True, blank=True)
    donation_made_to_political_party = models.BooleanField(default=False)
    donation_amount = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deductions.service_request.id} - Section 80ETTAU Donation"


class Section80C(models.Model):
    deductions = models.ForeignKey(Deductions, on_delete=models.CASCADE, related_name='section_80c')
    investment = models.CharField(max_length=50, null=True, blank=True,choices=[('ppf', 'ppf'),
                                                                                ('nsc', 'nsc'),
                                                                                ('elss', 'elss'),
                                                                                ('life insurance', 'life insurance'),
                                                                                ('tution fees', 'tution fees'),
                                                                                ('others', 'others')])
    amount = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deductions.service_request.id} - Section 80c Donation"


class Section80D(models.Model):
    deductions = models.OneToOneField(Deductions, on_delete=models.CASCADE, related_name='section_80d')
    self_family_non_senior_citizen = models.IntegerField(null=True, blank=True)
    parents_senior_citizen = models.IntegerField(null=True, blank=True)
    parents_non_senior_citizen = models.IntegerField(null=True, blank=True)
    self_senior_citizen = models.IntegerField(null=True, blank=True)
    preventive_health_checkup = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.deductions.service_request.id} - Section 80c Donation"


class Section80DFile(models.Model):

    section_80d = models.ForeignKey(Section80D, on_delete=models.CASCADE, related_name='section_80d_documents')
    file = models.FileField(upload_to=section_80d_file, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.section_80d.deductions.service_request.id} - {self.uploaded_at}"


class ReviewFilingCertificate(models.Model):
    REVIEW_STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('resubmission', 'Resubmission'),
        ('done', 'Done'),
    ]

    FILING_STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('filed', 'Filed'),
        ('resubmitted', 'Resubmitted'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resubmission', 'Resubmission'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='ITR_review_filing_certificate'
    )

    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )

    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_ITR_review_filing_certificate')

    review_certificate = models.FileField(upload_to=review_filing_certificate,
                                          null=True, blank=True)
    review_certificate_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        null=True,
        blank=True,
        default=None
    )

    filing_status = models.CharField(
        max_length=20,
        choices=FILING_STATUS_CHOICES,
        null=True,
        blank=True,
        default=None
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        null=True,
        blank=True,
        default=None
    )
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_ITR_review_filing_certificate')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_ITR_review_filing_certificate')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.review_certificate_status or "No Review Status"


def calculate_completion_percentage(instance, exclude_fields=None):
    exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at', 'service_request', 'service_task']
    total_fields = 0
    filled_fields = 0

    for field in instance._meta.fields:
        if field.name in exclude_fields:
            continue
        total_fields += 1
        value = getattr(instance, field.name)
        if value not in [None, '', []]:
            filled_fields += 1

    if total_fields == 0:
        return 0
    return round((filled_fields / total_fields) * 100)


@receiver(post_save, sender=PersonalInformation)
def sync_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()




