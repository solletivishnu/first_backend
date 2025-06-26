from django.urls import path
from . import views

urlpatterns = [

    # Proposed Company Details
    path('create-proposed-company-details/', views.create_proposed_company_details,
         name='create_proposed_company_details'),  # POST, GET
    path('proposed-company-details-by-service-request/', views.proposed_company_details_by_service_request,
         name='proposed_company_details_by_service_request'),  # GET
    path('proposed-company-detail/<int:id>/', views.proposed_company_detail,
         name='proposed_company_detail'),  # GET, PUT, DELETE

    # Registered Office Address
    path('create-registered-office-address/', views.create_registered_office_address,
         name='create_registered_office_address'),  # POST, GET
    path('registered-office-address-by-service-request/', views.registered_office_address_by_service_request,
         name='registered_office_address_by_service_request'),  # GET
    path('registered-office-address-details/<int:id>/', views.registered_office_address_details,
         name='registered_office_address_details'),  # GET, PUT, DELETE

    # Authorized & Paid-Up Capital
    path('create-authorized-paid-up-capital/', views.create_authorized_paid_up_capital,
         name='create_authorized_paid_up_capital'),  # POST, GET
    path('authorized-paid-up-capital-by-service-request/', views.authorized_paid_up_capital_by_service_request,
         name='authorized_paid_up_capital_by_service_request'),  # GET
    path('authorized-paid-up-capital-detail/<int:id>/', views.authorized_paid_up_capital_detail,
         name='authorized_paid_up_capital_detail'),  # GET, PUT, DELETE

    # Directors
    path('directors/', views.directors_list, name='directors_list'),
    path('directors/<int:pk>/', views.directors_detail, name='directors_detail'),
    path('directors/by-request/', views.get_directors_data, name='get_directors_data'),


    # Shareholders main object list/create (like Directors)
    path('shareholders/', views.shareholders_list, name='shareholders_list'),

    # Shareholders GET by service_request_id or service_task
    path('shareholders/by-request/', views.get_shareholders_data, name='get_shareholders_data'),

    # ShareholdersDetails GET, PUT, DELETE (like DirectorsDetails)
    path('shareholders/<int:pk>/', views.shareholders_detail, name='shareholders_detail'),


    # Review Filing Certificate
    path('create-review-filing-certificate/', views.create_review_filing_certificate,
         name='create_review_filing_certificate'),  # POST, GET
    path('review-filing-certificate-by-service-request/', views.review_filing_certificate_by_service_request,
         name='review_filing_certificate_by_service_request'),  # GET
    path('review-filing-certificate/<int:id>/', views.review_filing_certificate_detail,
         name='review_filing_certificate_detail'),  # GET, PUT, DELETE


    # Service Request Full Data
    path('service-requests-company-incorporation/<int:service_request_id>/full-data/',
         views.get_service_request_full_details, name='get_full_data_by_service_request'),

    # Service Request Tasks by Category
    path('service-request-section-data', views.get_service_request_tasks_by_category,
         name='get_service_request_section_data')

]