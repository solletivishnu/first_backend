from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .models import ServiceRequest, Service, ServicePlan, Context  # Adjust as per your app
from .service_serializers import *  # Optional if using serializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_new_service_request(request):
    """
    API endpoint to create a new ServiceRequest using serializer's save()
    """
    serializer = ServiceRequestCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    try:
        request_obj = serializer.save()
        return Response({
            'success': True,
            'message': 'Service request created successfully!',
            'service_request_id': request_obj.id
        }, status=201)
    except (Service.DoesNotExist, ServicePlan.DoesNotExist, Context.DoesNotExist, Users.DoesNotExist) as e:
        return Response({'error': str(e)}, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=500)