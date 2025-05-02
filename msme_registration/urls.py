from django.urls import path
from .views import *

urlpatterns = [
    path('registrations/', msme_registration_list_create, name='msme_registration_list_create'),
    path('registrations/<int:pk>/', msme_registration_detail_update_delete,
         name='msme_registration_detail_update_delete'),
    path('registrations/service-request/<int:service_request_id>/', service_request_with_msme,
         name='service_request_with_msme'),
]
