from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('invoicing-profiles/', views.get_invoicing_profile, name='get-invoicing-profile'),
    path('invoicing-profile-check/', invoicing_profile_exists, name='invoicing-profile-exists'),
    path('invoicing-profiles/create/', views.create_invoicing_profile, name='create-invoicing-profile'),
    path('invoicing-profiles/<int:pk>/update/', views.update_invoicing_profile, name='update-invoicing-profile'),
    path('invoicing-profiles/delete/', views.delete_invoicing_profile, name='delete-invoicing-profile'),
    path('customer_profiles/create/', create_customer_profile, name='create-customer-profile'),
    path('customer_profiles/', get_customer_profile, name='get-customer-profile'),
    path('customer_profiles/update/<int:id>/', update_customer_profile, name='update_customer_profile'),
    path('customer_profiles/delete/<int:id>', delete_customer_profile, name='delete-customer-profile'),
    path('api/v1/goods-services/create/', create_goods_service, name='create-goods-service'),

    # Retrieve a specific goods or service entry
    path('goods-services/<int:pk>', retrieve_goods_service, name='retrieve-goods-service'),

    # Update an existing goods or service entry
    path('goods-services/<int:id>/update/', update_goods_service, name='update-goods-service'),

    # Delete an existing goods or service entry
    path('goods-services/<int:id>/delete/', remove_goods_service, name='remove-goods-service'),

    path('invoice-create', create_invoice, name='create_invoice'),

    path('invoice-retrieve', retrieve_invoices, name='retrieve_invoices'),

    path('invoice-update/<int:invoice_id>/', update_invoice, name='update_invoice'),

    path('invoice-delete/<int:invoice_id>/', delete_invoice, name='delete_invoice'),

    path('create-pdf/<int:id>',views.createDocument),

    path('invoice-stats', get_invoice_stats, name='invoice-stats'),

    path('detail-invoice', get_invoices, name='get_invoices'),

    path('individual-invoice/<int:id>/', get_invoice_by_id, name='get_invoice_by_id'),

    path('latest/<int:invoicing_profile_id>/', latest_invoice_id, name='latest-invoice-number'),

    path('filter-invoices', filter_invoices, name='filter_invoices'),

    path('receipt', create_customer_invoice_receipt, name='create_customer_invoice_receipt'),

    path('receipt-get/', get_customer_invoice_receipts, name='get_customer_invoice_receipts'),

    path('receipt-update/<int:receipt_id>/', update_customer_invoice_receipt, name='update_customer_invoice_receipt'),

    path('receipt-delete/<int:receipt_id>/', delete_customer_invoice_receipt, name='delete_customer_invoice_receipt'),

    path('invoice-wave-off/<int:invoice_id>', wave_off_invoice, name='wave_off_invoice'),

    path('invoice-formats/', invoice_format_list, name='invoice_format_list'),

    path('invoice-formats/<int:pk>/', invoice_format_detail, name='invoice_format_detail'),

]

