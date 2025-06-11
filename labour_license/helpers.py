import os
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from usermanagement.models import Context, ServiceRequest  # Update this import as per your project


# class IsPlatformContext(BasePermission):
#     message = "This action is only allowed in a platform context."
#
#     def has_permission(self, request, view):
#         user = request.user
#         active_context_id = getattr(user, 'active_context_id', None)
#
#         if not active_context_id:
#             self.message = "User does not have an active context."
#             return False
#
#         try:
#             context = Context.objects.get(id=active_context_id)
#         except Context.DoesNotExist:
#             self.message = "Active context not found."
#             return False
#
#         if not context.is_platform_context:
#             self.message = "This action is only allowed in a platform context."
#             return False
#
#         request.context = context  # Attach context for use in views
#         return True


class IsPlatformOrAssociatedUser(BasePermission):
    message = "Access denied. You must be a platform user or associated with a service request in this context."

    def has_permission(self, request, view):
        user = request.user
        active_context_id = getattr(user, 'active_context_id', None)

        if not active_context_id:
            self.message = "User does not have an active context."
            return False

        # Check if platform context
        try:
            context = Context.objects.get(id=active_context_id)
        except Context.DoesNotExist:
            self.message = "Active context not found."
            return False

        if context.is_platform_context:
            return True

        # Check if user is associated with any service request in this context
        associated_request_exists = ServiceRequest.objects.filter(
            context_id=active_context_id
        ).filter(
            user_id=user.id
        ).exists() or ServiceRequest.objects.filter(
            context_id=active_context_id
        ).filter(
            assignee_id=user.id
        ).exists() or ServiceRequest.objects.filter(
            context_id=active_context_id
        ).filter(
            reviewer_id=user.id
        ).exists()

        if associated_request_exists:
            return True

        self.message = "You do not have permission to access this context."
        return False


def business_identity_structure_pan(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'business_identity_pan', filename)


def signatory_details_aadhar_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.signatory_details.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'signatory_details_aadhar_image',
                        filename)


def signatory_details_pan_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.signatory_details.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'signatory_details_pan_image',
                        filename)


def signatory_details_photo_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.signatory_details.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'signatory_details_photo_image',
                        filename)


def business_location_address_proof(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'business_location_address_proof',
                        filename)


def business_location_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_location_rental_agreement', filename)


def business_location_bank_statement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'business_location_bank_statement',
                        filename)


def additional_business_space_address_proof(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_location_proof_id = str(instance.business_location_proofs.id)
    service_request_id = str(instance.business_location_proofs.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id, business_location_proof_id,
                        'additional_business_space_address_proof', filename)


def additional_business_space_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_location_proof_id = str(instance.business_location_proofs.id)
    service_request_id = str(instance.business_location_proofs.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id, business_location_proof_id,
                        'additional_business_space_rental_agreement', filename)


def business_registration_documents_certificate_of_incorporation(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_documents_certificate_of_incorporation', filename)


def business_registration_documents_memorandum_of_articles(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_documents_memorandum_of_articles', filename)


def business_registration_documents_local_language_name_board_photo_business(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_documents_name_board_photo_business', filename)


def business_registration_documents_authorization_letter(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_documents_authorization_letter', filename)


def review_filing_certificate(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request.id)
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'review_filing_certificate', filename)

