from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import logging
from rest_framework import status
from django.db import transaction, DatabaseError
from .models import EventManagement
from .serializers import EventManagementSerializer
from rest_framework.response import Response
from datetime import date
from django.db.models import Prefetch

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """
    Create a new event.

    **Method:** POST
    **Auth:** Employee must be authenticated (JWT/session)

    **Request Body (JSON)**:
    ```json
    {
        "payroll": 1,
        "title": "Quarterly Meeting",
        "description": "Review Q3 objectives",
        "date": "2025-09-15",
        "time": "10:00:00",
        "applicable_to": [1, 2],
        "is_birthday": false,
        "employee": null
    }
    ```

    **Responses**:
    * `201 CREATED` – Event created successfully
    * `400 BAD REQUEST` – Validation errors
    * `500 INTERNAL SERVER ERROR` – Database error
    """
    serializer = EventManagementSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                event = serializer.save()
                logger.info(f"Event created: {event.id} by user {request.user.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except DatabaseError as e:
            logger.error(f"Database error while creating event: {str(e)}")
            return Response({"error": "Database error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Invalid data for event creation: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_events_by_payroll_id(request, payroll_id):
    """
    List all upcoming events for a given payroll, including birthdays.

    - Birthdays recur yearly and are adjusted to the next upcoming date.
    - Normal events are shown only if scheduled for today or in the future.
    - Results are sorted chronologically by upcoming date.
    - Adds `location_names` (list[str]) for each event's `applicable_to` M2M.

    **Method:** GET
    **Auth:** Employee must be authenticated

    **Path Parameter**:
    - `payroll_id` (int): ID of the payroll organization
    """
    try:
        today = date.today()

        # Prefetch M2M to avoid N+1; only pull the fields we need
        events = (
            EventManagement.objects
            .filter(payroll_id=payroll_id)
            .prefetch_related('applicable_to')
            .order_by('id')
        )

        upcoming_events = []

        for event in events:
            if event.is_birthday:
                birthday_this_year = event.date.replace(year=today.year)
                event.upcoming_date = (
                    birthday_this_year if birthday_this_year >= today
                    else birthday_this_year.replace(year=today.year + 1)
                )
            else:
                if event.date < today:
                    continue
                event.upcoming_date = event.date

            upcoming_events.append(event)

        # Sort by computed upcoming date
        upcoming_events.sort(key=lambda e: e.upcoming_date)

        # Build response, injecting upcoming date and location names
        data = []
        for e in upcoming_events:
            serialized = EventManagementSerializer(e).data

            # Show the next upcoming date (for birthdays: this/next year)
            serialized['date'] = e.upcoming_date

            # Add location names from M2M (adjust field name if different)
            serialized['applicable_to'] = list(
                e.applicable_to.values_list('location_name', flat=True)
            )

            # (Optional) also include location IDs if useful on FE
            # serialized['location_ids'] = list(e.applicable_to.values_list('id', flat=True))

            data.append(serialized)

        if not data:
            return Response({"message": "No upcoming events found."}, status=status.HTTP_200_OK)

        return Response(data, status=status.HTTP_200_OK)

    except DatabaseError as e:
        logger.error(f"Database error while fetching events: {str(e)}")
        return Response({"error": "Database error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_event(request, event_id):
    """
    Update an existing event by its ID.

    **Method:** PUT
    **Auth:** Employee must be authenticated

    **Path Parameter**:
    - `event_id` (int): ID of the event to update

    **Request Body (partial JSON allowed)**:
    ```json
    {
        "title": "Updated Title",
        "description": "Updated description",
        "date": "2025-09-20"
    }
    ```

    **Responses**:
    * `200 OK` – Event updated successfully
    * `400 BAD REQUEST` – Validation errors
    * `404 NOT FOUND` – Event not found
    * `500 INTERNAL SERVER ERROR` – Database error
    """
    try:
        event = EventManagement.objects.get(id=event_id)
    except EventManagement.DoesNotExist:
        logger.warning(f"Event not found: {event_id}")
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventManagementSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                event = serializer.save()
                logger.info(f"Event updated: {event.id} by user {request.user.id}")
                return Response(serializer.data, status=status.HTTP_200_OK)
        except DatabaseError as e:
            logger.error(f"Database error while updating event: {str(e)}")
            return Response({"error": "Database error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Invalid data for event update: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_event(request, event_id):
    """
    Delete an event by its ID.

    **Method:** DELETE
    **Auth:** Employee must be authenticated

    **Path Parameter**:
    - `event_id` (int): ID of the event to delete

    **Responses**:
    * `204 NO CONTENT` – Event deleted successfully
    * `404 NOT FOUND` – Event not found
    * `500 INTERNAL SERVER ERROR` – Database error
    """
    try:
        event = EventManagement.objects.get(id=event_id)
        event.delete()
        logger.info(f"Event deleted: {event_id} by user {request.user.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    except EventManagement.DoesNotExist:
        logger.warning(f"Event not found for deletion: {event_id}")
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
    except DatabaseError as e:
        logger.error(f"Database error while deleting event: {str(e)}")
        return Response({"error": "Database error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_event(request, event_id):
    """
    Retrieve a specific event by its ID.

    **Method:** GET
    **Auth:** Employee must be authenticated

    **Path Parameter**:
    - `event_id` (int): ID of the event

    **Responses**:
    * `200 OK` – Event retrieved successfully
    * `404 NOT FOUND` – Event not found
    """
    try:
        event = EventManagement.objects.get(id=event_id)
        serializer = EventManagementSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except EventManagement.DoesNotExist:
        logger.warning(f"Event not found: {event_id}")
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
