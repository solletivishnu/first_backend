from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_task_list, name='service-task-list'),                     # GET all, POST create
    path('<int:pk>/', views.service_task_detail, name='service-task-detail'),        # GET specific
    path('<int:pk>/update/', views.service_task_update, name='service-task-update'),  # PUT update
    path('<int:pk>/delete/', views.service_task_delete, name='service-task-delete'),  # DELETE
    path('service-task/<int:service_request_id>/', views.service_task_list_by_service_request_id, name='service-task-list-by-service-request-id'),  # GET all tasks by service request ID
]
