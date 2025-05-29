from django.urls import path
from . import views

urlpatterns = [
    # Business Identity Structure
    path('business-identity/', views.business_identity_structure_list, name='business_identity_list'),
    path('business-identity/<int:pk>/', views.business_identity_structure_detail, name='business_identity_detail'),

    # Signatory Details
    path('signatory-details/', views.signatory_details_list, name='signatory_details_list'),
    path('signatory-details/<int:pk>/', views.signatory_details_detail, name='signatory_details_detail'),

    # Business Location Proofs
    path('business-location/', views.business_location_proofs_list, name='business_location_list'),
    path('business-location/<int:pk>/', views.business_location_proofs_detail, name='business_location_detail'),

    # Additional Space Business
    path('additional-space/', views.additional_space_business_list, name='additional_space_list'),
    path('additional-space/<int:pk>/', views.additional_space_business_detail, name='additional_space_detail'),
    path('additional-space/view', views.get_additional_space_business_details, name='get_additional_space_business_details'),

    # Business Registration Documents
    path('registration-documents/', views.business_registration_documents_list,
         name='registration_documents_list'),
    path('registration-documents/<int:pk>/', views.business_registration_documents_detail,
         name='registration_documents_detail'),

    # Review Filing Certificate
    path('review-filing/', views.review_filing_certificate_list, name='review_filing_list'),
    path('review-filing/<int:pk>/', views.review_filing_certificate_detail, name='review_filing_detail'),

    path('business-identity/by-request-or-task', views.get_business_identity_structure,
         name='business_identity_by_request_or_task'),


    # Signatory Details
    path('signatory-details/by-request', views.get_signatory_details,
         name='signatory_by_request'),


    # Business Location Proofs
    path('business-location/by-request-or-task', views.get_business_location_proofs,
         name='business_location_by_request_or_task'),


    # Business Registration Documents
    path('registration-documents/by-request-or-task', views.get_business_registration_documents,
         name='registration_documents_by_request_or_task'),


    # Review Filing Certificate
    path('review-filing/by-request-or-task', views.get_review_filing_certificate,
         name='review_filing_by_request_or_task'),
]
