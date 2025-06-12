from django.urls import path
from . import views

urlpatterns = [
    # Basic Business Info
    path('basic-business-info/', views.basic_business_info_list_create, name='basic_business_info_list_create'),
    path('basic-business-info/by-service-request/', views.basic_business_info_by_service_request,
         name='basic_business_info_by_service_request'),
    path('basic-business-info/<int:pk>/', views.basic_business_info_detail, name='basic_business_info_detail'),

    # Registration Info
    path('registration-info/', views.registration_info_list_create, name='registration_info_list_create'),
    path('registration-info/by-service-request/', views.registration_info_by_service_request,
         name='registration_info_by_service_request'),
    path('registration-info/<int:pk>/', views.registration_info_detail,
         name='registration_info_detail'),

    # Principal Place Details
    path('principal-place-details/', views.principal_place_details_list_create,
         name='principal_place_details_list_create'),
    path('principal-place-details/by-service-request/', views.principal_place_details_by_service_request,
         name='principal_place_details_by_service_request'),
    path('principal-place-details/<int:pk>/', views.principal_place_details_detail,
         name='principal_place_details_detail'),

    # Promoter Signatory Details
    path('promoter-signatory-details/', views.upsert_promoter_signatory_data,
         name='promoter_signatory_details_upsert'),

    path('promoter-signatory-details/by-service-request/', views.get_promoter_signatory_data,
         name='promoter_signatory_details_get'),

    path('promoter-signatory-details/<int:pk>/update/', views.update_promoter_signatory_data,
         name='promoter_signatory_details_update'),

    path('promoter-signatory-info/<int:pk>/delete/', views.promoter_signatory_info_delete,
         name='promoter_signatory_info_delete'),

    # GSTReview Filing Certificate
    path('gst-review-filing-certificate/', views.gst_review_filing_certificate_list_create,
         name='gst_review_filing_certificate_list_create'),
    path('gst-review-filing-certificate/by-service-request/', views.gst_review_filing_certificate_by_service_request,
         name='gst_review_filing_certificate_by_service_request'),
    path('gst-review-filing-certificate/<int:pk>/', views.gst_review_filing_certificate_detail,
         name='gst_review_filing_certificate_detail'),

    # Service Request Full Data
    path('service-requests-gst/<int:service_request_id>/full-data/', views.get_service_request_full_details,
         name='get_full_data_by_service_request'),
    # Service Request Tasks by Category
    path('service-request-section-data', views.get_service_request_tasks_by_category,
         name='get_service_request_section_data')
]