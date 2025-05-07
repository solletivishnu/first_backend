from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .models import ServiceRequest, Service, ServicePlan, Context  # Adjust as per your app
from .serializers import *
import razorpay
from Tara.settings.default import RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET
from .service_serializers import *  # Optional if using serializer

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_new_service_request(request):
    """
    API endpoint to create a new ServiceRequest using serializer's save()
    """
    service_id = request.data.get('service_id')
    context_id = request.data.get('context_id')
    plan_id = request.data.get('plan_id')
    added_by_id = request.data.get('user_id')
    if not all([service_id, context_id, plan_id, added_by_id]):
        return Response({'error': 'Missing required fields'}, status=400)
    try:
        context = Context.objects.get(id=context_id)
        plan = ServicePlan.objects.get(id=plan_id)
        added_by = Users.objects.get(id=added_by_id)
        service = Service.objects.get(id=service_id)
    except (Context.DoesNotExist, ServicePlan.DoesNotExist, Users.DoesNotExist, Service.DoesNotExist) as e:
        return Response({'error': str(e)}, status=404)

    data = {
        "context_id": context_id,
        "service_id": service_id,
        "user_id": added_by_id,
        "plan_id": plan_id,
    }

    serializer = ServiceRequestCreateSerializer(data=data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    try:
        request_obj = serializer.save()

        try:
            service_request = ServiceRequest.objects.get(id=request_obj.id)

            if service_request.status != 'initiated':
                return Response({"error": "Payment not allowed. Service already processed."},
                                status=status.HTTP_400_BAD_REQUEST)

            if plan.service.id != service_request.service.id:
                return Response({"error": "Selected plan does not belong to the requested service."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Update plan selection
            service_request.plan = plan
            service_request.save()

            amount = int(plan.amount * 100)  # Amount in paisa

            try:
                old_payments = ServicePaymentInfo.objects.filter(
                    service_request=service_request.id,
                    status__iexact='initiated',
                    captured="no",
                    is_latest="yes"
                )
                print("[DEBUG] About to check if old payments exist")
                if old_payments.exists():
                    print("[DEBUG] Old payments found, updating...")
                    old_payments.update(is_latest=False)
                else:
                    print("[DEBUG] No old payments to update.")
            except Exception as e:
                print("EXCEPTION OCCURRED:", str(e))
                import traceback
                print(traceback.format_exc())

            # ✅ Step 2: Create a new Razorpay order
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "type": "service",
                    "service_payment_id": str(service_request.id),
                    "context_id": str(context.id),
                    "added_by": str(added_by.id)
                }
            })

            # ✅ Step 3: Save new payment info
            order_id = razorpay_order.get('id')
            if not order_id:
                raise ValueError("Razorpay order creation failed: no order ID returned.")

            serializer = ServicePaymentInfoSerializer(data={
                'user': added_by.id,
                'service_request': service_request.id,
                'plan': plan.id,
                'context': context.id,
                'amount': plan.amount,
                'razorpay_order_id': order_id,
                'status': 'initiated',
                'is_latest': 'yes'
            })

            if serializer.is_valid():
                serializer.save()
                print("[DEBUG] Payment info created:", serializer.data)
            else:
                print("[ERROR] Payment creation failed:", serializer.errors)
                return Response({"error": serializer.errors}, status=400)

            return Response({
                "message": "Razorpay order created successfully.",
                'service_request_id': request_obj.id,
                "order_id": razorpay_order['id'],
                "amount": amount,
                "currency": "INR",
                "key_id": RAZORPAY_CLIENT_ID,

            }, status=status.HTTP_200_OK)

        except ServiceRequest.DoesNotExist:
            return Response({"error": "ServiceRequest not found."}, status=status.HTTP_404_NOT_FOUND)
        except ServicePlan.DoesNotExist:
            return Response({"error": "ServicePlan not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to create Razorpay order: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (Service.DoesNotExist, ServicePlan.DoesNotExist, Context.DoesNotExist, Users.DoesNotExist) as e:
        return Response({'error': str(e)}, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=500)