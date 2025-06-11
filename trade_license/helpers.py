import os


def business_identity_structure_pan(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'business_identity_pan', filename)


def signatory_details_aadhar_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'signatory_details_aadhar_image',
                        filename)


def signatory_details_pan_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'signatory_details_pan_image',
                        filename)


def signatory_details_passport(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'signatory_details_passport_photo',
                        filename)


def promoter_or_directors_aadhaar(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.signatory_details.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'promoter_or_directors_aadhaar',
                        filename)


def promoter_or_directors_pan(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.signatory_details.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'promoter_or_directors_pan',
                        filename)


def promoter_or_directors_passport_photo(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.signatory_details.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'promoter_or_directors_passport_photo',
                        filename)


def business_location_address_proof(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'business_location_address_proof',
                        filename)


def business_location_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'business_location_rental_agreement', filename)


def business_location_bank_statement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Trade License', service_request_id, 'business_location_bank_statement',
                        filename)


def additional_business_space_address_proof(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_location_proof_id = str(instance.business_locations.id)
    service_request_id = str(instance.business_locations.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id, business_location_proof_id,
                        'additional_business_space_address_proof', filename)


def additional_business_space_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_location_proof_id = str(instance.business_locations.id)
    service_request_id = str(instance.business_locations.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id, business_location_proof_id,
                        'additional_business_space_rental_agreement', filename)


def business_registration_documents_certificate_of_incorporation(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'business_registration_documents_coi', filename)


def business_registration_documents_photo_of_premises(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'business_registration_documents_photo_of_premises', filename)


def business_registration_documents_property_tax_receipt(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'business_registration_documents_property_tax_receipt', filename)


def business_registration_documents_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'business_registration_documents_rental_agreement', filename)


def trade_license_document(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'trade_license_document', filename)


def review_filing_certificate(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Trade License', service_request_id,
                        'review_filing_certificate', filename)
