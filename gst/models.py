from Tara.settings.default import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from djongo.models import ArrayField, EmbeddedField, JSONField
from .helpers import *
from usermanagement.models import *
from django.db import models

# Create your models here.

class BasicDetails(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    legal_name = models.CharField(max_length=255)
    pan = models.CharField(max_length=15)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    email = models.EmailField()
    mobile = models.BigIntegerField()

    def __str__(self):
        return self.legal_name

class BusinessDetails(models.Model):
    option = [
        ('yes', 'Yes'),
        ('no', 'NO')
    ]
    gst = models.ForeignKey(BasicDetails, on_delete=models.CASCADE, related_name='BusinessDetails')
    legal_name = models.CharField(max_length=255)
    pan = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255)
    constitution = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    voluntary = models.CharField(max_length=5,choices=option)
    casual = models.CharField(max_length=5,choices=option)
    composition = models.CharField(max_length=5,choices=option)
    commencement = models.DateField()
    gst_have = models.CharField(max_length=5,choices=option)
    gst_details = JSONField(default = dict)

    def __str__(self):
        return self.legal_name

class Partner(models.Model):
    gst = models.ForeignKey(BasicDetails, on_delete=models.CASCADE, related_name='partner_details')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    father_first_name = models.CharField(max_length=100)
    father_middle_name = models.CharField(max_length=100, blank=True, null=True)
    father_last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")])
    designation = models.CharField(max_length=100)
    pan_number = models.CharField(max_length=10)
    address = JSONField(default=dict)
    name_of_premises = models.CharField(max_length=100)

    def __str__(self):
        return "{} - {}".format(self.first_name, self.last_name)

class BusinessDocuments(models.Model):

    gst = models.ForeignKey(BasicDetails, on_delete=models.CASCADE, related_name='business_document')
    business_pan = models.FileField(upload_to=upload_document)
    director_pan = models.FileField(upload_to=upload_document)
    photo = models.FileField(upload_to=upload_document)
    aadhaar_card = models.FileField(upload_to=upload_document, null=True, blank=True)
    nature_of_business = models.TextField()

    def __str__(self):
        return "Business Document {}".format(self.business_pan)

class PrincipalPlaceDetails(models.Model):
    ADDRESS_DOCUMENT_CHOICES = [
        ('Electricity Bill', 'Electricity Bill'),
        ('Lease deed/Rental agreement', 'Lease Deed/Rental Agreement'),
        ('Property tax receipt', 'Property Tax Receipt'),
    ]

    OWNERSHIP_TYPE_CHOICES = [
        ('own', 'Own'),
        ('rented', 'Rented'),
        ('lease', 'Lease'),
    ]

    gst = models.ForeignKey(BasicDetails, on_delete=models.CASCADE, related_name='principal_place')
    address = JSONField(default=dict)
    possession_nature = models.CharField(max_length=255,choices=OWNERSHIP_TYPE_CHOICES, blank=True, null=True)
    address_proof = models.CharField(max_length=255, choices=ADDRESS_DOCUMENT_CHOICES,blank=True, null=True)
    address_proof_file = models.FileField(upload_to=upload_principal_document, blank=True, null=True)
    noc_file = models.FileField(upload_to=upload_principal_document, blank=True, null=True)
    incorporationCert_file = models.FileField(upload_to=upload_principal_document, blank=True, null=True)

    def __str__(self):
        return "Partner {} - {}".format(self.gst, self.possession_nature)