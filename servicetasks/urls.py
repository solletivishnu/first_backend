from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_task_list, name='service-task-list'),                     # GET all, POST create
    path('<int:pk>/', views.service_task_detail, name='service-task-detail'),        # GET specific
    path('<int:pk>/update/', views.service_task_update, name='service-task-update'),  # PUT update
    path('<int:pk>/delete/', views.service_task_delete, name='service-task-delete'),  # DELETE
    path('service-task/<int:service_request_id>/', views.service_task_list_by_service_request_id,
         name='service-task-list-by-service-request-id'),  # GET all tasks by service request ID
    path('tasks/<int:task_id>/subtasks/', views.list_subtasks, name='list_subtasks'),
    path('subtasks/', views.create_subtask, name='create_subtask'),
    path('subtasks/<int:subtask_id>/', views.retrieve_subtask, name='retrieve_subtask'),
    path('subtasks/<int:subtask_id>/update/', views.update_subtask, name='update_subtask'),
    path('subtasks/<int:subtask_id>/delete/', views.delete_subtask, name='delete_subtask'),
]
