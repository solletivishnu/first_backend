from django.urls import path
from . import views
from . import tax_paid_details_views
from . import salary_income_views
from . import other_income_views
from . import house_property_income_views
from . import interest_income_views
from . import dividend_views
from . import family_pension_views
from . import gift_income_views
from . import foreign_income_views
from . import winning_income_views
from . import agriculture_income
from . import section_80g_views
from . import section_80ettattbu_views
from . import section_80c_views
from . import deductions
from . import section_80d_views
from . import nri_views
from . import capital_gains_views
from . import capital_gains_funds_details_views
from . import other_capital_gains_views
from . import business_professional_income_views
from . import section_80ee_views
from . import section_80e_views
from . import section_80ddb_views
from . import section_80_eeb_views

urlpatterns = [
    # Unified POST and PUT API for TaxPaidDetails and document uploads
    path('tax-paid-details/create-or-update/', tax_paid_details_views.upsert_tax_paid_details,
         name='tax_paid_details_create_or_update'),

    # Retrieve TaxPaidDetails by service_request and group files by document_type
    path('tax-paid-details/', tax_paid_details_views.tax_paid_details_view,
         name='tax_paid_details_view'),

    # Delete a specific file (also deletes from S3)
    path('tax-paid-details/files/<int:file_id>/delete/', tax_paid_details_views.delete_tax_paid_file,
         name='delete_tax_paid_file'),

    path('personal-information/', views.personal_information_list,
         name='personal_information_list'),

    # Retrieve, update, or delete a specific PersonalInformation by primary key
    path('personal-information/<int:pk>/', views.personal_information_detail,
         name='personal_information_detail'),

    path('personal-information/by-request-or-task', views.personal_information_by_service_request,
         name='personal_information_by_service_request'),

    # Salary Income Details
    path('salary-income/', salary_income_views.salary_income_list,
         name='salary_income_list_create'),
    path('salary-income/<int:pk>/', salary_income_views.salary_income_detail,
         name='salary_income_detail_update'),
    path('salary-documents/files/<int:pk>/delete/', salary_income_views.delete_salary_document,
         name='delete_salary_document_file'),
    path('salary-documents-count/<int:income_id>/', salary_income_views.salary_document_summary,
         name='salary_document_summary'),
    path('salary-income/by-request-or-task', salary_income_views.salary_income_by_service_request,
         name='salary_income_by_service_request'),

    path('other-income-details/', other_income_views.other_income_details_list,
         name='other_income_details_list'),
    path('other-income-details/<int:pk>/', other_income_views.other_income_details_detail,
         name='other_income_details_detail'),
    path('other-income-details/by-request-or-task', other_income_views.other_income_details_by_service_request,
         name='other_income_details_by_service_request'),
    path('other-income-details/<int:pk>/delete', other_income_views.delete_other_income_info,
         name="delete_other_income_info"),

    path('other-income-documents/', other_income_views.add_other_income_document,
         name='add_other_income_document'),
    path('other-income-document/<int:pk>/', other_income_views.add_other_income_document,
         name='update_or_delete_other_income_document'),

    # Capital Gains
    path('capital-gains/upsert/', capital_gains_views.upsert_capital_gains_details,
         name='upsert_capital_gains_details'),
    path('capital-gains/view/', capital_gains_views.get_capital_gains_details,
         name='get_capital_gains_details'),
    path('capital-gains/add-property/', capital_gains_views.add_capital_gains_property,
         name='add_capital_gains_property'),
    path('capital-gains/delete-property/<str:file_type>/<int:property_id>/',
         capital_gains_views.delete_capital_gains_property_file,
         name='delete_capital_gains_property_file'),
    path('capital-gains/delete-property/<int:pk>/', capital_gains_views.delete_capital_gains_property,
         name='delete_capital_gains_property'),

    path('capital-gains/update-property/<int:property_id>/', capital_gains_views.update_capital_gains_property,
         name='update_capital_gains_property'),

    # Capital Gains Equity Mutual Fund
    path('capital-gains/equity-mutual-fund/submit/',
         capital_gains_funds_details_views.upsert_equity_mutual_fund_with_files,
         name='upsert_equity_mutual_fund_with_files'),
    path('capital-gains/equity-mutual-fund/<int:service_request_id>/',
         capital_gains_funds_details_views.get_equity_mutual_fund_details, name='get_equity_mutual_fund_details'),
    path('capital-gains/equity-mutual-fund/<int:service_request_id>/delete/',
         capital_gains_funds_details_views.delete_equity_mutual_fund, name='delete_equity_mutual_fund'),
    path('capital-gains-equity-mutual-fund/files/<int:file_id>/delete/',
         capital_gains_funds_details_views.delete_equity_mutual_fund_file, name='delete_equity_mutual_fund_file'),

    # Business Professional Income
    path('business-professional-income/', business_professional_income_views.business_professional_income_upsert,
         name='upsert_business_professional_income'),
    path('business-professional-income/<int:service_request_id>/',
         business_professional_income_views.get_business_professional_income,
         name='get_business_professional_income'),
    path('business-professional-income/<int:pk>/delete/',
         business_professional_income_views.delete_business_professional_income,
         name='delete_business_professional_income'),
    path('business-professional-income/files/<int:file_id>/delete/',
         business_professional_income_views.delete_business_professional_income_file,
         name='delete_business_professional_income_file'),

    path('other-capital-gains/with-files/', other_capital_gains_views.upsert_other_capital_gains_with_files,
         name='upsert_other_capital_gains_with_files'),

    # Get details of Other Capital Gains by service_request ID
    path('other-capital-gains/<int:service_request_id>/', other_capital_gains_views.get_other_capital_gains_details,
         name='get_other_capital_gains_details'),

    # Delete entire Other Capital Gains record by service_request ID
    path('other-capital-gains/delete/<int:service_request_id>/', other_capital_gains_views.delete_other_capital_gains,
         name='delete_other_capital_gains'),

    # Delete a specific document by file ID
    path('other-capital-gains/document/<int:file_id>/delete/',
         other_capital_gains_views.delete_other_capital_gains_file,
         name='delete_other_capital_gains_file'),

    path('house-property-details/upsert/', house_property_income_views.upsert_house_property_details,
         name='upsert_house_property_details'),
    path('house-property-details/view/', house_property_income_views.house_property_details_view,
         name='house_property_details_view'),
    path('house-property-details/<str:file_type>/<int:service_request_id>/delete/',
         house_property_income_views.delete_house_property_file,
         name='delete_house_property_file'),
    path('house-property-details/<int:pk>/delete', house_property_income_views.delete_house_property,
         name='delete_house_property'),

    # InterestIncome endpoints
    path('interest-income/upsert/', interest_income_views.upsert_interest_income, name='upsert_interest_income'),
    path('interest-income/view/', interest_income_views.get_interest_income, name='get_interest_income'),

    # InterestIncomeDocument endpoints
    path('interest-income-doc/add/', interest_income_views.add_interest_income_document,
         name='add_interest_income_document'),
    path('interest-income-doc/files/<int:document_id>/delete/', interest_income_views.delete_interest_income_document,
         name='delete_interest_income_document'),
    path('interest-income-doc/<int:document_id>/update/', interest_income_views.update_interest_income_document,
         name='update_interest_income_document'),
    path('interest-income-doc/view', interest_income_views.list_interest_income_documents,
         name='list_interest_income_documents'),

    # GiftIncome APIs
    path('gift-income/upsert/', gift_income_views.upsert_gift_income_details,
         name='upsert_gift_income'),  # POST create or update
    path('gift-income/view/', gift_income_views.get_gift_income_details,
         name='get_gift_income'),  # GET by service_request

    # GiftIncomeDocument APIs
    path('gift-income-document/add/', gift_income_views.add_gift_income_document,
         name='add_gift_income_document'),  # POST add doc
    path('gift-income-document/<int:document_id>/update/', gift_income_views.update_gift_income_document,
         name='update_gift_income_document'),  # PUT update doc
    path('gift-income-document/files/<int:document_id>/delete/', gift_income_views.delete_gift_income_document,
         name='delete_gift_income_document'),  # DELETE doc
    path('gift-income-document/view/', gift_income_views.get_gift_income_documents,
         name='get_gift_income_document'),  # GET by service_request

    # DividendIncome APIs
    path('dividend-income/upsert/', dividend_views.upsert_dividend_income,
         name='upsert_dividend_income'),  # POST create or update
    path('dividend-income/view/', dividend_views.get_dividend_income,
         name='get_dividend_income'),   # GET by service_request

    # DividendIncomeDocument APIs
    path('dividend-income-document/add/', dividend_views.add_dividend_income_document,
         name='add_dividend_income_document'),  # POST add doc
    path('dividend-income-document/<int:document_id>/update/', dividend_views.update_dividend_income_document,
         name='update_dividend_income_document'),  # PUT update doc
    path('dividend-income-document/files/<int:document_id>/delete/', dividend_views.delete_dividend_income_document,
         name='delete_dividend_income_document'),  # DELETE doc
    path('dividend-income-document/view/', dividend_views.list_dividend_income_documents,
         name='list_dividend_income_document'),  # GET by service_request

    path('family-pension-income/upsert/', family_pension_views.upsert_family_pension_income,
         name='upsert_family_pension_income'),  # POST (create or update)
    path('family-pension-income/view/', family_pension_views.get_family_pension_income,
         name='get_family_pension_income'),     # GET (retrieve)

    # Family Pension Income Documents
    path('family-pension-income-documents/', family_pension_views.add_family_pension_income_document,
         name='add_family_pension_income_document'),  # POST (create)
    path('family-pension-income-documents/<int:document_id>/',
         family_pension_views.update_family_pension_income_document,
         name='update_family_pension_income_document'),  # PUT (update)
    path('family-pension-income-documents/files/<int:document_id>/delete/',
         family_pension_views.delete_family_pension_income_document,
         name='delete_family_pension_income_document'),  # DELETE
    path('family-pension-income-documents/view/', family_pension_views.get_family_pension_income_documents,
         name='get_family_pension_income_documents'),  # GET (retrieve by service_request)

    # Foreign Income APIs
    path('foreign-income/upsert/', foreign_income_views.upsert_foreign_income, name='upsert_foreign_income'),
    path('foreign-income/view/', foreign_income_views.get_foreign_income, name='get_foreign_income'),

    # ForeignIncomeInfo APIs
    path('foreign-income-info/add/', foreign_income_views.add_foreign_income_info, name='add_foreign_income_info'),
    path('foreign-income-info/<int:document_id>/update/', foreign_income_views.update_foreign_income_info,
         name='update_foreign_income_info'),
    path('foreign-income-info/<int:document_id>/delete/', foreign_income_views.delete_foreign_income_info,
         name='delete_foreign_income_info'),
    path('foreign-income-info/', foreign_income_views.get_foreign_income_info_list,
         name='get_foreign_income_info_list'),

    # Review Filing Certificate
    path('review-filing/', views.review_filing_certificate_list, name='review_filing_list'),
    path('review-filing/<int:pk>/', views.review_filing_certificate_detail, name='review_filing_detail'),
    path('review-filing/by-request-or-task', views.get_review_filing_certificate,
         name='review_filing_by_request_or_task'),

    # WinningIncome
    path('winning-income/upsert/', winning_income_views.upsert_winning_income, name='upsert_winning_income'),
    path('winning-income/view/', winning_income_views.get_winning_income, name='get_winning_income'),

    # WinningIncomeDocuments
    path('winning-income-docs/add/', winning_income_views.add_winning_income_document,
         name='add_winning_income_document'),
    path('winning-income-docs/<int:document_id>/update/', winning_income_views.update_winning_income_document,
         name='update_winning_income_document'),
    path('winning-income-docs/<int:document_id>/delete/', winning_income_views.delete_winning_income_document,
         name='delete_winning_income_document'),
    path('winning-income-docs/', winning_income_views.get_winning_income_documents,
         name='get_winning_income_documents'),

    # AgricultureIncome
    path('agriculture-income/upsert/', agriculture_income.upsert_agriculture_income, name='upsert_agriculture_income'),
    path('agriculture-income/', agriculture_income.get_agriculture_income, name='get_agriculture_income'),

    # AgricultureIncomeDocument
    path('agriculture-income-docs/add/', agriculture_income.add_agriculture_income_document,
         name='add_agriculture_income_document'),
    path('agriculture-income-docs/<int:document_id>/update/', agriculture_income.update_agriculture_income_document,
         name='update_agriculture_income_document'),
    path('agriculture-income-docs/<int:document_id>/delete/', agriculture_income.delete_agriculture_income_document,
         name='delete_agriculture_income_document'),
    path('agriculture-income-docs/', agriculture_income.get_agriculture_income_documents,
         name='get_agriculture_income_documents'),

    # Deductions
    path('deductions/upsert/', deductions.upsert_deductions, name='upsert_deductions'),
    path('deductions/', deductions.get_deductions, name='get_deductions'),

    path('section-80g/add/', section_80g_views.add_section_80g, name='add_section_80g'),
    path('section-80g/<int:pk>/update/', section_80g_views.update_section_80g, name='update_section_80g'),
    path('section-80g/<int:pk>/delete/', section_80g_views.delete_section_80g, name='delete_section_80g'),
    path('section-80g/', section_80g_views.list_section_80g, name='list_section_80g'),

    path(
        'section-80ettattbu/',
        section_80ettattbu_views.section_80ettattbu_list,
        name='section_80ettattbu_list'
    ),
    # retrieve, update, delete
    path(
        'section-80ettattbu/<int:pk>/',
        section_80ettattbu_views.section_80ettattbu_detail,
        name='section_80ettattbu_detail'
    ),

    # section 80c
    path(
        'section-80c/',
        section_80c_views.section_80c_list,
        name='section_80c_list'
    ),
    # retrieve, update, delete
    path(
        'section-80c/<int:pk>/',
        section_80c_views.section_80c_detail,
        name='section_80c_detail'
    ),

    path('section-80c-files/<int:file_id>/', section_80c_views.delete_section_80c_file, name='delete_section_80c_file'),

    path(
            'section-80d/full/',
            section_80d_views.upsert_section_80d_with_files,
            name='upsert_section_80d_with_files'
        ),
    # Retrieve & Delete Section80D
    path('section-80d/', section_80d_views.get_section_80d,    name='get_section_80d'),
    path('section-80d/<int:pk>/', section_80d_views.delete_section_80d, name='delete_section_80d'),

    # List & Delete Section80D files
    path('section-80d-files/', section_80d_views.list_section_80d_files, name='list_section_80d_files'),
    path('section-80d/files/<int:file_id>/delete/', section_80d_views.delete_section_80d_file, name='delete_section_80d_file'),

    path('service-requests-itr/<int:service_request_id>/full-data/', views.get_service_request_full_data,
         name='get_service_request_full_data'),

    path('nri-salary-details/upsert/', nri_views.upsert_nri_salary_details, name='upsert-nri-salary-details'),
    path('nri-salary-details/view/', nri_views.nri_salary_details_view, name='view-nri-salary-details'),
    path('nri-salary-details/files/<int:file_id>/delete/', nri_views.delete_nri_salary_file,
         name='delete-nri-salary-file'),

    path('service-request-section-data', views.get_service_request_section_data,
         name='get_service_request_section_data'),

    path('section-80ee/upsert/', section_80ee_views.upsert_section80ee_with_files, name='upsert-section80ee'),
    path('section-80ee/details/<int:deductions_id>/', section_80ee_views.get_section80ee_details,
         name='get-section80ee-details'),
    path('section-80ee/<int:deductions_id>/delete/', section_80ee_views.delete_section80ee, name='delete-section80ee'),
    path('section-80ee/files/<int:document_id>/delete/', section_80ee_views.delete_section80ee_document,
         name='delete_section80ee_document'),

    path('section-80e/', section_80e_views.upsert_section80e_with_files, name='upsert-section80e'),
    path('section-80e/details/<int:deductions_id>/', section_80e_views.get_section80e_details, name='get-section80e'),
    path('section-80e/<int:deductions_id>/delete/', section_80e_views.delete_section80e, name='delete-section80e'),
    path('section-80e/files/<int:document_id>/delete/', section_80e_views.delete_section80e_document,
         name='delete-section80e-documents'),

    path('section-80ddb/upsert/', section_80ddb_views.upsert_section80ddb_with_files),
    path('section-80ddb/details/<int:deductions_id>/', section_80ddb_views.get_section80ddb_details),
    path('section-80ddb/<int:deductions_id>/delete/', section_80ddb_views.delete_section80ddb),
    path('section-80ddb/files/<int:file_id>/delete/', section_80ddb_views.delete_section80ddb_file),

    path('section-80eeb/upsert/', section_80_eeb_views.upsert_section80eeb_with_files),
    path('section-80eeb/details/<int:deductions_id>/', section_80_eeb_views.get_section80eeb_details),
    path('section-80eeb/<int:deductions_id>/delete/', section_80_eeb_views.delete_section80eeb),
    path('section-80eeb/files/<int:file_id>/delete/', section_80_eeb_views.delete_section80eeb_file),

]

# Note: Ensure that the views and serializers are properly defined in their respective modules.
