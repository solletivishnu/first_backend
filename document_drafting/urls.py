from django.urls import path
from . import views

urlpatterns = [

    path('document-drafts-exists/<int:context_id>/', views.user_document_draft_is_exist, name='document-drafts-exists'),
    path('document-drafts-create', views.user_document_draft_list_create),
    path('document-drafts/<int:pk>/', views.user_document_draft_detail),

    # Category and Event URLs
    path('categories/', views.category_list_create),
    path('categories/<int:pk>/', views.category_detail),

    path('events/', views.events_list_create),
    path('events/<int:pk>/', views.events_detail),

    # Document and Document Fields URLs
    path('documents/', views.document_list_create),
    path('documents/<int:pk>/', views.document_detail),

    path('document-fields/', views.document_fields_list_create),
    path('document-fields/<int:pk>/', views.document_fields_detail),
    path('document-fields-template/<int:document_id>/', views.document_fields_by_document),
    path('document-fields-and-template/<int:id>/', views.document_template_and_fields),

    # Context Wise Events and Documents URLs
    path('context-events/<int:event_instance>/', views.context_wise_event_and_document, name='context-events'),
    path('context-wise-event-document-create/', views.context_wise_event_and_document_list_create,
         name='context-events-list-create'),
    path('context-wise-event-document/<int:pk>/', views.context_wise_event_and_document_detail,
            name='context-events-detail'),
    path('create-events/', views.draft_document_by_event, name='create-events'),

    # Document Drafts Data URLs
    path('document-drafts-details/', views.draft_document_details_create),
    path('document-drafts-details/<int:pk>/', views.draft_document_details),


    path('category-wise-event-list/<int:category_id>/', views.category_filter_events, name='category-list'),
    path('category-or-events-wise-document-list/', views.category_or_event_wise_document_list,
         name='event-wise-document-list'),
    path('document-list/<int:context_id>/', views.document_status_list, name='document-status-list'),
    path('my-events-list/', views.my_events_list, name='my-events-list'),

    path('documents-summary-by-context/', views.document_summary_by_context, name='documents-summary-by-context'),
    path('filtered-documents-by-status/', views.filter_documents_by_status, name='filtered-documents'),


    path('favourites/', views.favourite_document_list_create, name='favourite-document-list-create'),
    path('favourites/<int:pk>/', views.favourite_document_detail, name='favourite-document-detail'),
    path('favourites/by-draft/<int:draft_id>/', views.favourite_documents_by_draft,
         name='favourite-documents-by-draft'),

    path('context/<int:context_id>/recent-documents/', views.recent_documents_by_context,
         name='recent-documents-by-context'),
    path('context/<int:context_id>/recent-events/', views.recent_events_by_context,
         name='recent-events-by-context'),
]