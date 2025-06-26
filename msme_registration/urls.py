from django.urls import path
from . import views

urlpatterns = [
    # Personal Information URLs
    path('business-identity/', views.business_identity_list, name='business_identity_list'),
    path('business-identity/<int:pk>/', views.business_identity_detail, name='business_identity_detail'),
    path('business-identity/by-service-request/', views.business_identity_by_service_request,
         name='business_identity_by_service_request'),

    # Business Classification URLs
    path('business-classification/', views.business_classification_list, name='business_classification_list'),
    path('business-classification/<int:pk>/', views.business_classification_detail,
         name='business_classification_detail'),
    path('business-classification/by-service-request/', views.business_classification_by_service_request,
         name='business_classification_by_service_request'),

    # TurnOver Details URLs
    path('turnover-details/', views.turnover_declaration_list, name='turnover_details_list'),
    path('turnover-details/<int:pk>/', views.turnover_declaration_detail, name='turnover_details_detail'),
    path('turnover-details/by-service-request/', views.turnover_declaration_by_service_request,
         name='turnover_details_by_service_request'),

    # Registration Address Details URLs
    path('registration-address-details/', views.registered_address_list, name='registration_address_details_list'),
    path('registration-address-details/<int:pk>/', views.registered_address_detail,
         name='registration_address_details_detail'),
    path('registration-address-details/by-service-request/', views.registered_address_by_service_request,
         name='registration_address_details_by_service_request'),

    # Location Of Plant Or Unit URLs
    path('location-of-plant-or-unit/', views.location_of_plant_or_unit_list, name='location_of_plant_or_unit_list'),
    path('location-of-plant-or-unit/<int:pk>/', views.location_of_plant_or_unit_detail,
         name='location_of_plant_or_unit_detail'),
    path('location-of-plant-or-unit/by-service-request/', views.location_of_plant_or_unit_by_registration_address_id,
         name='location_of_plant_or_unit_by_registration_address_id'),

    # Review Filing Certificate URLs
    path('review-filing-certificate/', views.review_filing_certificate_list, name='review_filing_certificate_list'),
    path('review-filing-certificate/<int:pk>/', views.review_filing_certificate_detail,
         name='review_filing_certificate_detail'),
    path('review-filing-certificate/by-service-request/', views.get_review_filing_certificate,
         name='review_filing_certificate_by_service_request'),

    path('service-request-msme/<int:service_request_id>/full-data',views.get_msme_data_by_service_request,
         name='msme-data'),

    path('service-requests-msme-registration/<int:service_request_id>/full-data/',
         views.get_msme_full_data_by_service_request, name='get_full_data_by_service_request'),

    path('service-request-section-data',views.get_msme_tasks_using_section_name, name='get_msme_section_data'),

]