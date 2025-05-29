from django.urls import path
from . import views


urlpatterns = [
    path('business-identity/', views.business_identity_list, name='business_identity_list'),
    path('business-identity/<int:pk>/', views.business_identity_detail, name='business_identity_detail'),
    path('business-identity/by-request-or-task', views.get_business_identity,
         name='business_identity_by_request_or_task'),

    path('applicant-details/', views.applicant_detail_list, name='applicant_detail_list'),
    path('applicant-details/<int:pk>/', views.applicant_detail, name='applicant_detail'),
    path('applicant-details/by-request-or-task', views.get_applicant_detail, name='applicant_detail_by_request_or_task'),

    path('signatory-details/', views.signatory_detail_list, name='signatory_detail_list'),
    path('signatory-details/<int:pk>/', views.signatory_detail, name='signatory_detail'),
    path('signatory-details/by-request-or-task', views.get_signatory_detail, name='signatory_detail_by_request_or_task'),

    path('business-location/', views.business_location_list, name='business_location_list'),
    path('business-location/<int:pk>/', views.business_location_detail, name='business_location_detail'),
    path('business-location/by-request-or-task', views.get_business_location, name='business_location_by_request_or_task'),

    path('additional-space/', views.additional_address_detail_list, name='additional_address_detail_list'),
    path('additional-space/<int:pk>/', views.additional_address_detail, name='additional_address_detail'),

    path('trade-license-exist/', views.trade_license_list, name='trade_license_list'),
    path('trade-license-exist/<int:pk>/', views.trade_license_detail, name='trade_license_detail'),
    path('trade-license-exist/by-request-or-task', views.get_trade_license, name='trade_license_by_request_or_task'),

    path('business-documents/', views.business_document_detail_list, name='business_document_detail_list'),
    path('business-documents/<int:pk>/', views.business_document_detail, name='business_document_detail'),
    path('business-documents/by-request-or-task', views.get_business_document, name='business_document_by_request_or_task'),

    path('review-filing/', views.review_filing_certificate_list, name='review_filing_list'),
    path('review-filing/<int:pk>/', views.review_filing_certificate_detail, name='review_filing_detail'),
    path('review-filing/by-request-or-task', views.get_review_filing_certificate, name='review_filing_by_request_or_task'),
]
