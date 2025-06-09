from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ServiceTask
from servicetasks.models import ServiceTask, ServiceSubTask
from .serializers import ServiceTaskSerializer, ServiceTaskDetailedSerializer, ServiceSubTaskSerializer
from django.db import models


@api_view(['GET'])
def service_task_list(request):
    user = request.user

    if getattr(user, 'is_super_admin', False):  # ✅ Safe check
        tasks = ServiceTask.objects.all()
    else:
        tasks = ServiceTask.objects.filter(
            models.Q(assignee=user) |
            models.Q(reviewer=user) |
            models.Q(client=user)
        ).distinct()

    serializer = ServiceTaskDetailedSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def service_task_detail(request, pk):
    try:
        task = ServiceTask.objects.get(pk=pk)
    except ServiceTask.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ServiceTaskDetailedSerializer(task)
    return Response(serializer.data)


@api_view(['POST'])
def service_task_create(request):
    serializer = ServiceTaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
def service_task_update(request, pk):
    try:
        task = ServiceTask.objects.get(pk=pk)
    except ServiceTask.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ServiceTaskSerializer(task, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def service_task_delete(request, pk):
    user = request.user

    # ✅ Check if user is super admin
    if not getattr(user, 'is_super_admin', False):
        return Response({'error': 'You do not have permission to delete this task.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        task = ServiceTask.objects.get(pk=pk)
    except ServiceTask.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response({'message': 'Task deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def service_task_list_by_service_request_id(request, service_request_id):
    tasks = ServiceTask.objects.filter(service_request_id=service_request_id)
    serializer = ServiceTaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Service Subtasks

@api_view(['GET'])
def list_subtasks(request, task_id):
    subtasks = ServiceSubTask.objects.filter(parent_task_id=task_id)
    serializer = ServiceSubTaskSerializer(subtasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_subtask(request):
    serializer = ServiceSubTaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def retrieve_subtask(request, subtask_id):
    try:
        subtask = ServiceSubTask.objects.get(id=subtask_id)
        serializer = ServiceSubTaskSerializer(subtask)
        return Response(serializer.data)
    except ServiceSubTask.DoesNotExist:
        return Response({"error": "Subtask not found"}, status=404)


@api_view(['PUT', 'PATCH'])
def update_subtask(request, subtask_id):
    try:
        subtask = ServiceSubTask.objects.get(id=subtask_id)
        serializer = ServiceSubTaskSerializer(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except ServiceSubTask.DoesNotExist:
        return Response({"error": "Subtask not found"}, status=404)


@api_view(['DELETE'])
def delete_subtask(request, subtask_id):
    try:
        subtask = ServiceSubTask.objects.get(id=subtask_id)
        subtask.delete()
        return Response({"message": "Subtask deleted successfully"}, status=204)
    except ServiceSubTask.DoesNotExist:
        return Response({"error": "Subtask not found"}, status=404)


