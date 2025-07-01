from usermanagement.models import *
from msme_registration.helpers import *
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from usermanagement.models import ServiceRequest, Users
from servicetasks.models import ServiceTask
from .helpers import upload_bank_statement_or_cancelled_cheque_path, upload_official_address_proof_path
from docwallet.models import PrivateS3Storage

#MSME_Registration = ["BusinessIdentity", "BusinessClassificationInputs", "TurnoverAndInvestmentDeclaration",
# "RegisteredAddress", "MsmeReviewFilingCertificate"]


class BusinessIdentity(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='msme_business_identity_details')
    service_type = models.CharField(max_length=20,default="MSME Registration",editable=False)
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_msme_business_identity')
    organisation_type = models.CharField(max_length=100, blank=False)
    business_name = models.CharField(max_length=255, null=False, blank=False)
    pan_of_business_or_COI = models.FileField(upload_to= upload_pan_path, null=True,
                                              blank=True, storage=PrivateS3Storage())
    aadhar_of_signatory = models.FileField(upload_to= upload_aadhar_path, null=True,
                                           blank=True, storage=PrivateS3Storage())
    mobile_number = models.CharField(max_length=15, blank=True)
    email_id = models.EmailField(max_length=255, blank=True)
    Are_you_previously_registered_UAM = models.BooleanField(default=False, blank=True, null=True,
                                                            help_text="Check if previously registered under UAM")
    UAM_number = models.CharField(max_length=50, blank=True, null=True)
    has_business_commenced = models.BooleanField(default=False, blank=True, null=True,
                                                 help_text="Check if business has commenced")
    date_of_commencement = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='msme_bi_assignee'
    )
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='msme_bi_reviewer'
    )
    def save(self, *args, **kwargs):
        # Default to service_request values if isn't set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(BusinessIdentity, self).save(*args, **kwargs)

    def __str__(self):
        return self.business_name


class BusinessClassificationInputs(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='business_classification_details')
    service_type = models.CharField(max_length=20,default="MSME Registration",editable=False)
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_business_classification_details')
    MAJOR_ACTIVITY_CHOICES = [
        ('Manufacturing','Manufacturing'),
        ('Service', 'Service'),
    ]
    major_activity = models.CharField(
        max_length=20,
        choices=MAJOR_ACTIVITY_CHOICES,
        blank=True,
        default='Manufacturing',
    )
    nature_of_business = models.CharField(max_length=100, blank=True)
    nic_codes = models.JSONField(default=dict, blank=True, null=True)
    number_of_persons_employed = models.JSONField(default=dict, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')],
                              null=False, blank=False,default="in progress")
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_business_classification')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_business_classification')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(BusinessClassificationInputs, self).save(*args, **kwargs)


    def __str__(self):
        return "{} - {}".format(self.major_activity, self.nature_of_business)


#Turnover and Investment Declaration
GST_REGISTRATION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
    ('exempted', 'Exempted'),
]


class TurnoverAndInvestmentDeclaration(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                    related_name='turnover_details')
    service_type = models.CharField(max_length=20,default="MSME Registration",editable=False)
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                     related_name='service_task_turnover_details')
    turnover_in_inr = models.JSONField(default=dict, blank=True, null=True)
    investment_in_plant_and_machinery = models.IntegerField(blank=True, null=True)
    have_you_filed_itr_previous_year = models.BooleanField(default=False, blank=True, null=True,
                                                    help_text="Check if you have filed ITR for the previous year")
    are_you_registered_under_gst = models.CharField(max_length=10,choices=GST_REGISTRATION_CHOICES,
                                            blank=True,null=True)
    gst_certificate = models.FileField(upload_to=upload_gst_certificate_path, blank=True,
                                       null=True, storage=PrivateS3Storage())
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                        ('sent for approval', 'Sent for Approval'),('revoked', 'Revoked')],
                                         null=False, blank=False,default="in progress")
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_turnover_investment_declaration')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_turnover_investment_declaration')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(TurnoverAndInvestmentDeclaration, self).save(*args, **kwargs)

    def __str__(self):
        return "Turnover and Investment Declaration #{}".format(self.id)


# Registered Address
class RegisteredAddress(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='registered_address_details')
    service_type = models.CharField(max_length=20, default="MSME Registration", editable=False)
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_registered_address_details')
    official_address_of_enterprise = models.JSONField(null=True, blank=True)
    bank_statement_or_cancelled_cheque = models.FileField(upload_to=upload_bank_statement_or_cancelled_cheque_path,
                                                          blank=True, null=True, storage=PrivateS3Storage())
    official_address_of_proof = models.FileField(upload_to=upload_official_address_proof_path,
                                                 blank=True, null=True, storage=PrivateS3Storage())
    location_of_plant = models.BooleanField(default=False, blank=True, null=True,
                                            help_text="Check if you have a location of plant or unit")
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                    ('sent for approval', 'Sent for Approval'),('revoked', 'Revoked')],
                                    null=False, blank=False, default="in progress")
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_registered_address')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_registered_address')

    def save(self, *args, **kwargs):
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(RegisteredAddress, self).save(*args, **kwargs)

    def __str__(self):
        return "Enterprise Address #{}".format(self.id)


# Unit/plant address
class LocationOfPlantOrUnit(models.Model):
    registered_address = models.ForeignKey(RegisteredAddress, on_delete=models.CASCADE,
                                           related_name='location_of_plant_or_unit')
    unit_details = models.JSONField(null=True, blank=True)

    def __str__(self):
        if self.unit_details:
            name = self.unit_details.get("unit_name")
            return name or "Unnamed Unit"
        return "Unnamed Unit"


# Review and Filing Certificate
class MsmeReviewFilingCertificate(models.Model):
    service_type = models.CharField(max_length=20, default="MSME Registration", editable=False)
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                            related_name='msme_review_certificates')
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE, related_name='msme_review_tasks')

    REVIEW_STATUS_CHOICES = [('in progress', 'In Progress'), ('completed', 'Completed'),
                             ('sent for approval', 'Sent for Approval'),
                             ('revoked', 'Revoked')]
    FILING_STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('filed', 'Filed'),
        ('sent for approval', 'Sent for Approval'),
        ('resubmitted', 'Resubmitted'),
    ]
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resubmission', 'Resubmission'),
        ('sent for approval', 'Sent for Approval'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]
    review_certificate = models.FileField(upload_to=review_filing_certificate_path, null=True,
                                          blank=True, storage=PrivateS3Storage())
    review_certificate_status = models.CharField(max_length=20,choices=REVIEW_STATUS_CHOICES,
                                                 null=True, blank=True,default=None)

    draft_income_file = models.FileField(upload_to=draft_filing_certificate,
                                         null=True, blank=True, storage=PrivateS3Storage())
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
    assignee = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='msme_reviewfc_assignee'
    )
    reviewer = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='msme_reviewfc_reviewer'
    )

    status = models.CharField(
        max_length=20,
        choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                 ('sent for approval', 'Sent for Approval'), ('revoked', 'Revoked')],
        null=False, blank=False, default="in progress"
    )

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(MsmeReviewFilingCertificate, self).save(*args, **kwargs)

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


@receiver(post_save, sender=BusinessIdentity)
def sync_msme_business_identity_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=BusinessClassificationInputs)
def sync_msme_business_classification_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=TurnoverAndInvestmentDeclaration)
def sync_msme_turnover_investment_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=RegisteredAddress)
def sync_msme_registered_address_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=MsmeReviewFilingCertificate)
def sync_msme_review_filing_certificate_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=LocationOfPlantOrUnit)
def sync_registered_address_status(sender, instance, **kwargs):
    instance.registered_address.status = "in progress"
    instance.registered_address.save()
