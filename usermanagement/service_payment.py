import razorpay
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import ServiceRequest, ServicePaymentInfo
from Tara.settings.default import RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET
import hmac, hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ServicePaymentInfo, ServiceRequest, ServicePlan
import json
from rest_framework.permissions import AllowAny
from .serializers import *

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_razorpay_order_for_services(request):
    service_request_id = request.data.get('service_request_id')
    plan_id = request.data.get('plan_id')

    if not all([service_request_id, plan_id]):
        return Response({"error": "Both service_request_id and plan_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_request = ServiceRequest.objects.get(id=service_request_id, user=request.user)

        if service_request.status != 'initiated':
            return Response({"error": "Payment not allowed. Service already processed."},
                            status=status.HTTP_400_BAD_REQUEST)

        plan = ServicePlan.objects.get(id=plan_id)

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
                "service_payment_id": str(service_request.id)
            }
        })

        # ✅ Step 3: Save new payment info
        order_id = razorpay_order.get('id')
        if not order_id:
            raise ValueError("Razorpay order creation failed: no order ID returned.")

        serializer = ServicePaymentInfoSerializer(data={
            'user': request.user.id,
            'service_request': service_request.id,
            'plan': plan.id,
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
            "order_id": razorpay_order['id'],
            "amount": amount,
            "currency": "INR",
            "key_id": RAZORPAY_CLIENT_ID
        }, status=status.HTTP_200_OK)

    except ServiceRequest.DoesNotExist:
        return Response({"error": "ServiceRequest not found."}, status=status.HTTP_404_NOT_FOUND)
    except ServicePlan.DoesNotExist:
        return Response({"error": "ServicePlan not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Failed to create Razorpay order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @csrf_exempt
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def service_razorpay_webhook(request):
#     try:
#         webhook_secret = "servicetesting"
#         received_sig = request.headers.get('X-Razorpay-Signature')
#         print("[Webhook] Received Signature:", received_sig)
#
#         generated_sig = hmac.new(
#             webhook_secret.encode(),
#             request.body,
#             hashlib.sha256
#         ).hexdigest()
#
#         print("[Webhook] Generated Signature:", generated_sig)
#
#         if not hmac.compare_digest(received_sig, generated_sig):
#             print("[Webhook] Signature mismatch.")
#             return JsonResponse({'error': 'Signature mismatch'}, status=400)
#
#         data = json.loads(request.body)
#         print("[Webhook] Payload received:\n", json.dumps(data, indent=2))
#
#         if data.get('event') == 'payment.captured':
#             entity = data['payload']['payment']['entity']
#             payment_id = entity['id']
#             order_id = entity['order_id']
#             method = entity['method']
#
#             print(f"[Webhook] Payment Captured: payment_id={payment_id}, order_id={order_id}, method={method}")
#
#             payment = ServicePaymentInfo.objects.get(razorpay_order_id=order_id)
#             payment = ServicePaymentInfo.objects.get(razorpay_order_id=order_id)
#
#             payment.razorpay_payment_id = payment_id
#             payment.method = method
#             payment.status = 'captured'
#             payment.captured = 'yes'
#             payment.paid_at = timezone.now()
#             payment.save()
#
#         return JsonResponse({'status': 'ok'})
#
#     except ServicePaymentInfo.DoesNotExist:
#         print(f"[Webhook][ERROR] No payment found for Razorpay order_id: {order_id}")
#         return JsonResponse({'error': 'Payment record not found'}, status=404)
#
#     except Exception as e:
#         import traceback
#         print("[Webhook][ERROR] Exception occurred:", str(e))
#         print(traceback.format_exc())
#         return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def unified_razorpay_webhook(request):
    try:
        print("[Webhook] Received Razorpay webhook")
        webhook_secret = "servicetesting"
        received_sig = request.headers.get('X-Razorpay-Signature')

        generated_sig = hmac.new(
            webhook_secret.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()

        print(f"[Webhook] Received Signature: {received_sig}")
        print(f"[Webhook] Generated Signature: {generated_sig}")

        if not hmac.compare_digest(received_sig, generated_sig):
            print("[Webhook] Signature mismatch")
            return JsonResponse({'error': 'Signature mismatch'}, status=400)

        data = json.loads(request.body)
        print(f"[Webhook] Payload: {json.dumps(data, indent=2)}")

        if data.get('event') != 'payment.captured':
            print(f"[Webhook] Ignored event: {data.get('event')}")
            return JsonResponse({'status': 'ignored'}, status=200)

        entity = data['payload']['payment']['entity']
        notes = entity.get('notes', {})
        payment_id = entity['id']
        order_id = entity['order_id']
        method = entity['method']

        print(f"[Webhook] Processing payment_id={payment_id}, order_id={order_id}, method={method}, notes={notes}")

        payment_type = notes.get('type')

        if payment_type == 'service':
            return handle_service_payment(order_id, payment_id, method)
        elif payment_type == 'module':
            return handle_module_payment(notes, order_id, payment_id, method)
        else:
            print(f"[Webhook] Unknown payment type: {payment_type}")
            return JsonResponse({'error': 'Unknown payment type'}, status=400)

    except Exception as e:
        import traceback
        print("[Webhook][ERROR]:", traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


def handle_service_payment(order_id, payment_id, method):
    try:
        print(f"[ServicePayment] Fetching payment for order_id={order_id}")
        payment = ServicePaymentInfo.objects.get(razorpay_order_id=order_id)

        if payment.status == 'captured':
            print(f"[ServicePayment] Already captured for order_id={order_id}")
            return JsonResponse({'status': 'already processed'}, status=200)

        print("[ServicePayment] Marking payment as captured...")
        payment.razorpay_payment_id = payment_id
        payment.method = method
        payment.status = 'captured'
        payment.captured = 'yes'
        payment.paid_at = timezone.now()
        payment.save()

        if payment.service_request:
            payment.service_request.status = 'paid'
            payment.service_request.save()
            print(f"[ServicePayment] Updated ServiceRequest #{payment.service_request.id} to paid")

        return JsonResponse({'status': 'service payment processed'})
    except ServicePaymentInfo.DoesNotExist:
        print(f"[ServicePayment][ERROR] ServicePaymentInfo not found for order_id={order_id}")
        return JsonResponse({'error': 'ServicePaymentInfo not found'}, status=404)


def handle_module_payment(notes, order_id, payment_id, method):
    try:
        subscription_id = notes.get('subscription_id')
        context_id = notes.get('context_id')

        print(f"[ModulePayment] Looking for ModuleSubscription id={subscription_id}, context_id={context_id}")
        subscription = ModuleSubscription.objects.get(id=subscription_id, context_id=context_id)

        if subscription.status == 'active':
            print(f"[ModulePayment] Subscription already active for id={subscription_id}")
            return JsonResponse({'status': 'already active'}, status=200)

        print(f"[ModulePayment] Activating subscription...")
        subscription.status = 'active'
        subscription.payment_status = 'captured'
        subscription.payment_method = method
        subscription.razorpay_payment_id = payment_id
        subscription.paid_at = timezone.now()
        subscription.save()

        create_subscription_cycle(subscription)

        return JsonResponse({'status': 'module subscription processed'})
    except ModuleSubscription.DoesNotExist:
        print(f"[ModulePayment][ERROR] ModuleSubscription not found for id={subscription_id}, context={context_id}")
        return JsonResponse({'error': 'ModuleSubscription not found'}, status=404)


def create_subscription_cycle(subscription):
    try:
        print(f"[SubscriptionCycle] Creating cycle for subscription id={subscription.id}")
        with transaction.atomic():
            initial_feature_usage = {}
            if subscription.plan.features_enabled:
                for feature, details in subscription.plan.features_enabled.items():
                    if isinstance(details, dict) and 'limit' in details:
                        initial_feature_usage[feature] = 0

            SubscriptionCycle.objects.create(
                subscription=subscription,
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                amount=Decimal(str(subscription.plan.base_price)),
                is_paid='yes',
                feature_usage=initial_feature_usage
            )
            print("[SubscriptionCycle] Created successfully")
    except Exception as e:
        print(f"[SubscriptionCycle][ERROR] Failed to create cycle: {str(e)}")