from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from .models import SubscriptionCycle, ModuleUsageCycle, ModuleSubscription


def get_usage_entry(context_id, feature_key):
    try:
        # Get active subscription
        subscription = ModuleSubscription.objects.filter(
            context_id=context_id,
            status__in=["active", "trial"]
        ).first()

        if not subscription:
            return None, Response(
                {"error": "No active subscription found for this context."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get latest cycle
        cycle = SubscriptionCycle.objects.filter(subscription=subscription).order_by('-start_date').first()
        if not cycle:
            return None, Response(
                {"error": "No active subscription cycle found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch usage entry
        usage_entry = ModuleUsageCycle.objects.filter(
            cycle=cycle,
            feature_key=feature_key
        ).first()

        if not usage_entry:
            return None, Response(
                {"error": f"No usage data found for feature '{feature_key}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate usage limit
        if usage_entry.actual_count != "unlimited":
            if int(usage_entry.usage_count) >= int(usage_entry.actual_count):
                return None, Response(
                    {
                        "error": f"Usage limit reached for '{usage_entry.feature_key}'. "
                                 f"Please upgrade your subscription or contact the admin team to proceed."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return usage_entry, None

    except Exception as e:
        return None, Response(
            {"error": f"Failed to get usage entry: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def increment_usage(usage):
    """
    This updates the usage count after the action is completed.
    """
    if usage and usage.actual_count != "unlimited":
        usage.usage_count = str(int(usage.usage_count) + 1)
        usage.save(update_fields=['usage_count'])

