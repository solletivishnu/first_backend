from django.db import models
from Tara.settings.default import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from djongo.models import ArrayField, EmbeddedField, JSONField
from .helpers import *
from usermanagement.models import ServiceRequest, Users
from servicetasks.models import ServiceTask
from django.db.models.signals import post_save
from django.dispatch import receiver


class BusinessIdentityStructure(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='business_identity_structure')
    service_type = models.CharField(
        max_length=20,
        default="Labour License",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_business_identity')
    classification_of_establishment = models.CharField(max_length=255, null=False, blank=False)
    category_of_establishment = models.CharField(max_length=255, null=False, blank=False)
    legal_name_of_business = models.CharField(max_length=255, null=False, blank=False)
    nature_of_business = models.CharField(max_length=255, null=False, blank=False)
    business_pan = models.FileField(upload_to=business_identity_structure_pan,
                                    null=True, blank=True)
    date_of_commencement = models.DateField(null=False, blank=False)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_businesses')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_businesses')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.legal_name_of_business


class SignatoryDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='business_signatory_details')
    service_type = models.CharField(
        max_length=20,
        default="Labour License",
        editable=False
    )
    service_task = models.ForeignKey(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_signatory_details')
    name = models.CharField(max_length=255, null=False, blank=False)
    aadhar_image = models.FileField(upload_to=signatory_details_aadhar_image,
                                    null=True, blank=True)
    pan_image = models.FileField(
        upload_to=signatory_details_pan_image,
        null=True, blank=True)
    photo_image = models.FileField(
        upload_to=signatory_details_photo_image,
        null=True, blank=True)
    mobile_number = models.BigIntegerField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    residential_address = models.CharField(max_length=3, choices=[('yes', 'YES'), ('no', 'No')],
                                           null=False, blank=False)
    address = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_signatory')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_signatory')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BusinessLocationProofs(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='business_location_proofs')
    service_type = models.CharField(
        max_length=20,
        default="Labour License",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_business_locations_proof')
    principal_place_of_business = JSONField(default=dict)
    nature_of_possession = models.CharField(max_length=255, null=False, blank=False)
    address_proof = models.FileField(
        upload_to=business_location_address_proof,
        null=False, blank=False)
    rental_agreement = models.FileField(
        upload_to=business_location_rental_agreement,
        null=False, blank=False)
    bank_statement = models.FileField(
        upload_to=business_location_bank_statement,
        null=True, blank=True)
    additional_space = models.CharField(max_length=3, choices=[('yes', 'YES'), ('no', 'No')],
                                        null=False, blank=False)
    workplace = models.CharField(max_length=200, null=False, blank=False)

    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_businesses_location_proofs')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_businesses_location_proofs')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nature_of_possession


class AdditionalSpaceBusiness(models.Model):
    business_location_proofs = models.OneToOneField(BusinessLocationProofs, on_delete=models.CASCADE,
                                                    related_name='additional_space_business')
    address = JSONField(default=dict)
    nature_of_possession = models.CharField(max_length=255, null=False, blank=False)
    address_proof = models.FileField(
        upload_to=additional_business_space_address_proof,
        null=False, blank=False)
    rental_agreement = models.FileField(
        upload_to=additional_business_space_rental_agreement,
        null=False, blank=False)

    def __str__(self):
        return self.nature_of_possession


class BusinessRegistrationDocuments(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='business_registration_documents')
    service_type = models.CharField(
        max_length=20,
        default="Labour License",
        editable=False
    )
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_business_registration')
    certificate_of_incorporation = models.FileField(
        upload_to=business_registration_documents_certificate_of_incorporation,
        null=False, blank=False)
    memorandum_of_articles = models.FileField(
        upload_to=business_registration_documents_memorandum_of_articles,
        null=False, blank=False)
    local_language_name_board_photo_business = models.FileField(
        upload_to=business_registration_documents_local_language_name_board_photo_business,
        null=False, blank=False)
    authorization_letter = models.FileField(
        upload_to=business_registration_documents_authorization_letter,
        null=False, blank=False)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_businesses_registration_docs')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_businesses_registration_docs')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.certificate_of_incorporation


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
        related_name='review_filing_certificate'
    )

    service_type = models.CharField(
        max_length=20,
        default="Labour License",
        editable=False
    )

    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='service_task_review_filing_certificate')

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
                                 related_name='assigned_businesses_review_filing_certificate')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_businesses_review_filing_certificate')

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


@receiver(post_save, sender=BusinessIdentityStructure)
def sync_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()



