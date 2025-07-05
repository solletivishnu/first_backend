from django.urls import path
from . import views

urlpatterns = [
    # DocWallet API URLs
    path('context-docs', views.docwallet_list_create, name='docwallet-list-create'),
    path('context-docs/<int:pk>/', views.docwallet_detail, name='docwallet-detail'),

    # Folder API URLs
    path('folders/', views.folder_list_create, name='folder-list-create'),
    path('folders/<int:pk>/', views.folder_detail, name='folder-detail'),

    # Document API URLs
    path('documents/', views.document_list_create, name='document-list-create'),
    path('documents/<int:pk>/', views.document_detail, name='document-detail'),

    path('folders/<int:folder_id>/files/', views.list_folders_and_files, name='list-folders-and-files'),

    path('generate_presigned_url', views.documents_view, name='generate_presigned_url'),

    path('list_last_10_uploaded_files', views.retrieve_recent_files, name='list_last_10_uploaded_files'),

    path('delete_folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
    path('remove_file/<int:file_id>/', views.remove_document, name='remove_file_from_folder'),

    path('wallet-info', views.retrieve_docwallet_info, name='docwallet-info'),

    path('fetch-document', views.fetch_document_data, name='fetch_document_data'),

    path("files/search-autocomplete/", views.context_file_autocomplete),
    path("files/search/", views.context_file_filter),
]
