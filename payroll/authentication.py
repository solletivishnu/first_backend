from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework import exceptions
from .models import EmployeeCredentials


class EmployeeJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        employee_id = validated_token.get('employee_id')
        if not employee_id:
            raise InvalidToken("Token missing employee_id")

        try:
            return EmployeeCredentials.objects.get(employee__id=employee_id)
        except EmployeeCredentials.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such employee')
