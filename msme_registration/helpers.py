import os


# Business Identity
def upload_pan_path(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join(
        'service_requests', 'MSME Registration', service_request_id, 'business_identity_pan_or_coi', filename
    )


def upload_aadhar_path(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join(
        'service_requests', 'MSME Registration', service_request_id, 'business_identity_aadhar_of_signatory', filename
    )


# Msme Review Filing Certificate review_certificate field
def review_filing_certificate_path(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join(
        'service_requests', 'MSME Registration', service_request_id, 'review_filing_certificate', filename
    )


# Turnover And Investment Declaration
def upload_gst_certificate_path(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join(
        'service_requests', 'MSME Registration', service_request_id, 'turnover_gst_certificate', filename
    )


# Registered Address, units and location of plant or unit field
def upload_bank_statement_or_cancelled_cheque_path(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join(
        'service_requests', 'MSME Registration', service_request_id, 'bank_statement_or_cancelled_cheque', filename
    )


def upload_official_address_proof_path(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join(
        'service_requests', 'MSME Registration', service_request_id, 'rental_agreement_or_utility_bill', filename
    )


