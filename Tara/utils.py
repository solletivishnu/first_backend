from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from usermanagement.models import Users  # Assuming your user model is in user_management app
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
# from user_management.models import CustomGroup, CustomPermission, UserAffiliatedRole, Business, UserAffiliationSummary
from user_management.serializers import *
from rest_framework.fields import CharField
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import JsonResponse


User = get_user_model()  # Fetch the custom user model


def health_check(request):
    return JsonResponse({"status": "healthy"}, status=200)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email_or_user_name'
    user_type = CharField(required=True)

    def validate(self, attrs):
        # Get email or mobile from the input data
        email_or_user_name = attrs.get("email_or_user_name")
        password = attrs.get("password")
        user_type = attrs.get("user_type")

        # Ensure email_or_mobile and password are provided
        if not email_or_user_name or not password:
            raise AuthenticationFailed("Email/Mobile and password are required.")

        # Attempt to find the user by email or mobile
        if "@" in email_or_user_name:
            users = User.objects.filter(email__iexact=email_or_user_name)
            if not users.exists():
                raise AuthenticationFailed("No user found with the provided email.")
        else:
            users = User.objects.filter(user_name__iexact=email_or_user_name)
            if not users.exists():
                raise AuthenticationFailed("No user found with the provided username.")

        if user_type:
            users = users.filter(Q(user_type=user_type) | Q(user_type="TaraTeam"))

            # Check if any user exists after filtering by user_type
        if not users.exists():
            raise AuthenticationFailed("No user found with the provided user type.")

            # Iterate over the users to check the password
        for user in users:
            if check_password(password, user.password):
                # If password matches, proceed
                break
        else:
            # If no valid password match is found, raise error
            raise AuthenticationFailed("Invalid password. Please try again.")

        if not user.is_active:
            raise AuthenticationFailed("User account is not active. Please verify your email or mobile.")

        # if not user.check_password(password):
        #     raise AuthenticationFailed("Invalid password. Please try again.")

        # Ensure the user is active
        if not user.is_active:
            raise AuthenticationFailed("User account is not active. Please verify your email or mobile.")

        # Generate the refresh and access token
        refresh = self.get_token(user)

        # Check if UserKYC is completed
        user_kyc = False
        user_name = None
        if hasattr(user, 'userkyc'):  # Assuming `UserKYC` has a one-to-one or foreign key to `User`
            user_kyc_instance = user.userkyc
            user_name = user_kyc_instance.name
            user_kyc = True

            # if user_kyc_instance.is_completed:  # Assuming `is_completed` indicates KYC completion
            #     user.user_kyc = True  # Update the `user_kyc` field in the User model
            #     user.save(update_fields=['user_kyc'])  # Save only the `user_kyc` field
            #     user_kyc = True

        # Extract the date from created_on
        created_on_date = user.date_joined.date()

        # Retrieve the user's group
        user_roles = UserAffiliatedRole.objects.filter(
            user=user.id)
        # Map user types to their respective lists
        user_type_map = {
            'Individual': [],
            'CA': [],
            'ServiceProvider': [],
            'Business': [],
        }

        # Serialize and categorize data
        for item in UserGroupSerializer(user_roles, many=True).data:
            affiliated_data = item.get('affiliated', {})
            affiliated_data['flag'] = item.get('flag')
            user_type = affiliated_data.get('user_type')

            if user_type in user_type_map:
                if user_type == "Business":
                    business = Business.objects.filter(client=affiliated_data['id'])
                    business_data = UserBusinessRetrieveSerializer(business, many=True).data
                    user_type_map[user_type].extend(business_data)
                else:
                    user_type_map[user_type].append(affiliated_data)

        # try:
        #     user_affiliation_summary = UserAffiliationSummary.objects.get(user=user)  # Fetch a single UserGroup instance
        # except UserAffiliationSummary.DoesNotExist:
        #     raise ValueError("Something Wrong with this User, Please Connect Admin Team To Solve the Issue")

        business_exits = False

        # Customize the response data
        data = {
            'id': user.id,
            'email': user.email,
            'mobile_number': user.mobile_number,
            'user_name': user.user_name,
            'name': user.first_name + ' ' + user.last_name,
            'created_on': created_on_date,
            'user_type': user.user_type,
            'user_kyc': user_kyc,
            'individual_affiliated': list(user_type_map['Individual']),
            'ca_firm_affiliated': list(user_type_map['CA']),
            'service_provider_affiliated': list(user_type_map['ServiceProvider']),
            'business_affiliated': list(user_type_map['Business']),
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'service_request': user.service_request
        }
        if user.user_type == "Business":
            business_exists = Business.objects.filter(client=user).exists()
            data['business_exists'] = business_exists
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]  # Ensure this view is publicly accessible

    def post(self, request, *args, **kwargs):
        # Serialize the incoming request data
        print(request.data)
        serializer = self.get_serializer(data=request.data)

        # Prevent schema generation errors with Swagger
        swagger_fake_view = getattr(request, "swagger_fake_view", False)

        if swagger_fake_view:  # Skip processing if it's a Swagger fake view
            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            # Validate the data
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            # If validation fails, return an error response
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # Return the validated data along with tokens
        return Response(serializer.validated_data, status=status.HTTP_200_OK)