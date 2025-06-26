import os
from datetime import timedelta, date
import random


def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def gst_document_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'gst_documents', filename)


def lut_letter_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'lut_letters', filename)


def license_document_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'license_documents', filename)

def logo_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'logo', filename)


SERVICE_TASK_MAP = {
    "labour-license": [
        "Business Identity Structure",
        "Signatory Details",
        "Business Location Proofs",
        "Business Registration Documents",
        "Review Filing Certificate"
    ],
    "msme-registration": [
        "Business Identity",
        "Business Classification Inputs",
        "Turnover And InvestmentDeclaration",
        "Registered Address",
        "Review Filing Certificate"
    ],
    "trade-license": [
        "Business Identity",
        "Applicant Details",
        "Signatory Details",
        "Business Location",
        "Trade License Details",
        "Business Document Details",
        "Review Filing Certificate"
    ],
    "itr-filing": [
        "Personal Information",
        "Tax Paid Details",
        "Deductions",
        "Review Filing Certificate"
    ],
    "registration": [
        "Basic Business Info",
        "Registration Info",
        "Principal Place Details",
        "Promoter Signatory Details",
        "GST Review Filing Certificate"
    ],
    "private-limited":[
        "Proposed Company Details",
        "Registered Office Address",
        "Authorized PaidUp Share Capital",
        "Directors",
        "Shareholders",
        "Review Filing Certificate"
    ]
}


due_dates = {
    "labour-license": date.today() + timedelta(days=1),
    "trade-license": date.today() + timedelta(days=1),
    "itr-filing": date.today() + timedelta(days=1),
    "registration": date.today() + timedelta(days=7),
    "msme-registration": date.today() + timedelta(days=1),
    "private-limited": date.today() + timedelta(days=15),
}