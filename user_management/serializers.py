# from rest_framework import serializers
# from .models import User, UserKYC, FirmKYC, AddressModel
# from django.contrib.auth.models import *
# from .models import *
# import json
# from collections import OrderedDict
# from collections import defaultdict
# from django.utils.timezone import now
#
#
# class UserRegistrationSerializer(serializers.ModelSerializer):
#     """
#     Serializer for user registration.
#     Either email and password OR mobile number and password must be provided.
#     """
#     password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
#     email = serializers.EmailField(required=False, allow_null=True)
#     mobile_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
#     created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
#     user_type = serializers.CharField(required=False, allow_null=True)
#     first_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
#     last_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
#     is_active = serializers.BooleanField(default=False)
#     user_name = serializers.CharField(max_length=120, allow_null=False, allow_blank=False)
#     service_request = serializers.CharField(max_length=40, allow_null=False, allow_blank=False, default='')
#
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'mobile_number', 'password', 'created_by', 'user_type', 'user_name'
#                   , 'first_name', 'last_name', 'is_active', 'service_request')
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         mobile_number = attrs.get('mobile_number')
#
#         # Ensure only one of email or mobile number is provided
#         # if email and mobile_number:
#         #     raise serializers.ValidationError("Provide either email or mobile number, not both.")
#         if not email and not mobile_number:
#             raise serializers.ValidationError("At least one of email or mobile number must be provided.")
#
#         return attrs
#
#     def create(self, validated_data):
#         # Extract created_by if present; default to None
#         created_by = validated_data.get('created_by', None)
#         email = validated_data.get('email', None)
#         mobile_number = validated_data.get('mobile_number', None)
#         password = validated_data.get('password')
#         user_type = validated_data.get('user_type', None)
#         first_name = validated_data.get('first_name', '')
#         last_name = validated_data.get('last_name', '')
#         user_name = validated_data.get('user_name')
#         service_request = validated_data.get('service_request', '')
#
#         # Create the user with the provided data
#         user = User.objects.create_user(
#             email=email,
#             password=password,
#             mobile_number=mobile_number,
#             user_type=user_type,
#             first_name=first_name,
#             last_name=last_name,
#             user_name=user_name,
#             created_by=created_by,
#             service_request=service_request
#         )
#
#         return user
#
#
# class UserSerializer(serializers.ModelSerializer):
#     date_joined = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ['id', 'user_name', 'email', 'mobile_number',
#                   'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
#
#     def get_date_joined(self, obj):
#         return obj.date_joined.strftime('%d-%m-%Y')  # Format as dd-mm-yyyy
#
#
# class CustomPermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomPermission
#         fields = ['id', 'action_name', 'module_name', 'description']
#
#
# class CustomGroupSerializer(serializers.ModelSerializer):
#     permissions = serializers.SerializerMethodField()
#
#     class Meta:
#         model = CustomGroup
#         fields = ['id', 'name', 'permissions']
#
#     def get_permissions(self, obj):
#         grouped_permissions = defaultdict(list)
#         for perm in obj.permissions.all():
#             # Format each permission
#             grouped_permissions[perm.module_name].append({
#                 "id": perm.id,
#                 "key": perm.module_name,
#                 "label": perm.module_name.replace('_', ' ').title(),
#                 "description": perm.description,
#             })
#         return grouped_permissions
#
#     def create(self, validated_data):
#         permissions = validated_data.pop('permissions', [])
#         group = CustomGroup.objects.create(**validated_data)
#         group.permissions.set(permissions)  # Assign permissions
#         return group
#
#
# class CustomGroupSerializerData(serializers.ModelSerializer):
#     class Meta:
#         model = CustomGroup
#         fields = ['id', 'name']
#
#
# class UserAffiliatedDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'user_name', 'user_type']
#
#
# class UserGroupSerializer(serializers.ModelSerializer):
#     # group = serializers.PrimaryKeyRelatedField(
#     #     queryset=CustomGroup.objects.all(), required=False, allow_null=True
#     # )  # Handles foreign key relationship correctly
#
#     custom_permissions = CustomPermissionSerializer(many=True, required=False)
#
#     class Meta:
#         model = UserAffiliatedRole
#         fields = ['id', 'user', 'group', 'custom_permissions', 'added_on']
#
#     def create(self, validated_data):
#         """
#         Create and return a new `InvoicingProfile` instance, given the validated data.
#         """
#         instance = self.Meta.model(**validated_data)
#         instance.save()
#         return instance
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `InvoicingProfile` instance, given the validated data.
#         """
#         [setattr(instance, k, v) for k, v in validated_data.items()]
#         instance.save()
#         return instance
#
#
# class UserGroupSerializer(serializers.ModelSerializer):
#     affiliated = UserAffiliatedDataSerializer()  # Use the UserSerializer for the affiliated field
#     custom_permissions = CustomPermissionSerializer(many=True, required=False)
#
#     class Meta:
#         model = UserAffiliatedRole
#         fields = ['id', 'user', 'affiliated', 'group', 'custom_permissions', 'added_on', 'flag']
#
#     def to_representation(self, instance):
#         # Get the standard representation first
#         representation = super().to_representation(instance)
#
#         # Custom handling for affiliated if needed
#         affiliated_data = representation.get('affiliated', {})
#         # Optionally, manipulate or modify `affiliated_data` here if needed
#
#         return representation
#
#
# class UserActivationSerializer(serializers.Serializer):
#     token = serializers.CharField()
#
#
# class AddressSerializer(serializers.Serializer):
#     address_line1 = serializers.CharField(max_length=255, required=False)
#     address_line2 = serializers.CharField(max_length=255, required=False)
#     address_line3 = serializers.CharField(max_length=255, required=False, allow_blank=True)
#     pinCode = serializers.IntegerField(required=False, allow_null=True)
#     state = serializers.CharField(max_length=20, required=False)
#     city = serializers.CharField(max_length=20, required=False)
#     country = serializers.CharField(max_length=20, required=False)
#
#
# class BusinessSerializer(serializers.ModelSerializer):
#     entityType = serializers.CharField(max_length=50, required=False)
#     pan = serializers.CharField(max_length=15, required=False, default=None)
#     headOffice = serializers.JSONField(default=dict)
#
#     class Meta:
#         model = Business
#         fields = '__all__'
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Business` instance, given the validated data.
#         """
#         instance = self.Meta.model(**validated_data)
#         instance.save()
#         return instance
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Business` instance, given the validated data.
#         """
#         [setattr(instance, k, v) for k, v in validated_data.items()]
#         instance.save()
#         return instance
#
#
# class GSTDetailsSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = GSTDetails
#         fields = '__all__'
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Business` instance, given the validated data.
#         """
#         instance = self.Meta.model(**validated_data)
#         instance.save()
#         return instance
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Business` instance, given the validated data.
#         """
#         [setattr(instance, k, v) for k, v in validated_data.items()]
#         instance.save()
#         return instance
#
#
# class BusinessUserSerializer(serializers.ModelSerializer):
#     entityType = serializers.CharField(max_length=50, required=False)
#     pan = serializers.CharField(max_length=15, required=True)
#     headOffice = serializers.JSONField(default=dict)
#     gst_details = GSTDetailsSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Business
#         fields = '__all__'
#
#
# class UserBusinessRetrieveSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Business
#         fields = ['id', 'nameOfBusiness', 'entityType', 'client']
#
#
# class BusinessWithGSTSerializer(serializers.ModelSerializer):
#     gst_details = GSTDetailsSerializer(many=True, read_only=True)
#     headOffice = serializers.JSONField(default=dict)
#
#     class Meta:
#         model = Business
#         fields = ['id', 'nameOfBusiness', 'entityType', 'registrationNumber', 'pan', 'mobile_number', 'trade_name',
#                   'email', 'dob_or_incorp_date', 'gst_details', 'headOffice', 'headOffice', 'business_nature']
#
#
# class UserBusinessSerializer(serializers.ModelSerializer):
#     date_joined = serializers.SerializerMethodField()
#     business = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = [
#             'id', 'user_name', 'email', 'mobile_number',
#             'first_name', 'last_name', 'user_type',
#             'is_active', 'date_joined', 'business'
#         ]
#
#     def get_date_joined(self, obj):
#         return obj.date_joined.strftime('%d-%m-%Y')  # Format as dd-mm-yyyy
#
#     def get_business(self, obj):
#         # Fetch related Business objects
#         businesses = obj.business_clients_id.all()
#         return BusinessWithGSTSerializer(businesses, many=True).data
#
#
#
# class UsersKYCSerializer(serializers.ModelSerializer):
#     address = AddressSerializer(default={}, required=False)  # Nested serializer for address
#
#     class Meta:
#         model = UserKYC
#         fields = [
#             'id', 'user', 'pan_number', 'aadhaar_number', 'date', 'icai_number', 'address', 'name', 'have_firm'
#         ]
#         read_only_fields = ['user']  # Prevent modification of `user` field
#
#     def validate(self, data):
#         """
#         Validate data based on the user type.
#         """
#         user = self.context['request'].user  # Accessing the user from the request context
#
#         # Ensure user_type exists in the user model
#         if not hasattr(user, 'user_type'):
#             raise serializers.ValidationError("User type is missing.")
#
#         user_type = user.user_type
#         icai_number = data.get('icai_number')
#
#         # Ensure `icai_number` is None for individuals
#         if user_type == 'individual' and icai_number is not None:
#             raise serializers.ValidationError({
#                 "icai_number": "ICAI Number must be None for individual user type."
#             })
#
#         # Ensure `icai_number` is provided for CA firms
#         if user_type == 'cafirm' and not icai_number:
#             raise serializers.ValidationError({
#                 "icai_number": "ICAI Number is required for Chartered Accountant Firm."
#             })
#
#         return data
#
#     def create(self, validated_data):
#         """
#         Create a new `UserKYC` instance.
#         """
#         # Handle address field: if it's not provided, use default empty address
#         address_data = validated_data.pop('address', None)
#         if address_data is None:
#             address_data = {
#                 "address_line1": None,
#                 "address_line2": None,
#                 "address_line3": None,
#                 "pinCode": None,
#                 "state": None,
#                 "city": None,
#                 "country": None
#             }
#
#         # Create the UserKYC instance
#         user_details = UserKYC.objects.create(**validated_data, address=address_data)
#         return user_details
#
#     def update(self, instance, validated_data):
#         """
#         Update an existing `UserKYC` instance.
#         """
#         # Extract and handle address data
#         address_data = validated_data.pop('address', None)
#
#         # Update other fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#
#         # Update the address field if it's provided
#         if address_data:
#             instance.address = address_data
#
#         instance.save()
#         return instance
#
#
# class FirmKYCSerializer(serializers.ModelSerializer):
#     address = AddressSerializer(required=False)
#
#     class Meta:
#         model = FirmKYC
#         fields = [
#             'user', 'firm_name', 'firm_registration_number', 'firm_email', 'firm_mobile_number',
#             'number_of_firm_partners', 'address'
#         ]
#         read_only_fields = ['user']
#
#     def create(self, validated_data):
#         """
#         Create a new `UserKYC` instance.
#         """
#         # Check if 'address' is present in validated_data
#         if 'address' not in validated_data:
#             # If not present, set default address values
#             validated_data['address'] = {
#                 "address_line1": None,
#                 "address_line2": None,
#                 "address_line3": None,
#                 "pinCode": None,
#                 "state": None,
#                 "city": None,
#                 "country": None
#             }
#
#         # Create and save the UserKYC instance
#         user_details = FirmKYC.objects.create(**validated_data)
#
#         return user_details
#
#
# class UserUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['user_name', 'email', 'mobile_number', 'user_type', 'first_name', 'last_name', 'is_active']
#         # You can modify this list based on the fields you want to allow updating
#
#     def update(self, instance, validated_data):
#         # Perform the actual update for the instance
#         return super().update(instance, validated_data)
#
#
# class GroupSerializer(serializers.ModelSerializer):
#     # Customizing the id field to match the desired structure
#     id = serializers.IntegerField(source='pk', required=False)
#
#     class Meta:
#         model = Group  # Replace with your actual model
#         fields = ['id', 'name']
#
#     def to_representation(self, instance):
#         """
#         Customizing how the response data is serialized.
#         """
#         # Get the default representation of the model
#         representation = super().to_representation(instance)
#
#         # If you want to include the MongoDB _id as well:
#         representation['_id'] = {"$oid": str(instance.pk)}  # Converts the `pk` (primary key) to ObjectId format
#         return representation
#
#
# class PermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = ['id', 'name', 'codename', 'content_type']
#
#
# class ServicesMasterDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServicesMasterData
#         fields = '__all__'
#
#
# class ServiceDetailsSerializer(serializers.ModelSerializer):
#     service_type = serializers.PrimaryKeyRelatedField(queryset=ServicesMasterData.objects.all())
#     visa_application = serializers.PrimaryKeyRelatedField(queryset=VisaApplications.objects.all(), required=True)  # Include this line
#     service_name = serializers.ReadOnlyField(source='service_type.service_name')
#     last_updated_date = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ServiceDetails
#         fields = ['id', 'service_type', 'service_name', 'date', 'status', 'comments', 'quantity',
#                   'visa_application', 'last_updated_date']  # Ensure service_name is included
#
#     def get_last_updated_date(self, obj):
#         if obj.last_updated:
#             # Get only the date part from the datetime field
#             return obj.last_updated.date()
#         return None
#
#
#
# class VisaApplicationsSerializer(serializers.ModelSerializer):
#     # services = ServiceDetailsSerializer(many=True)
#
#     class Meta:
#         model = VisaApplications
#         fields = "__all__"
#
#
# class IndividualServiceDetailsSerializer(serializers.ModelSerializer):
#     service_type = serializers.PrimaryKeyRelatedField(queryset=ServicesMasterData.objects.all())
#     visa_application = serializers.PrimaryKeyRelatedField(queryset=VisaApplications.objects.all(), required=True)  # Include this line
#     service_name = serializers.ReadOnlyField(source='service_type.service_name')
#     last_updated_date = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ServiceDetails
#         fields = ['id', 'service_type', 'service_name', 'date', 'status', 'comments', 'quantity',
#                   'visa_application', 'last_updated_date']  # Ensure service_name is included
#
#     def get_last_updated_date(self, obj):
#         if obj.last_updated:
#             # Get only the date part from the datetime field
#             return obj.last_updated.date()
#         return None
#
#
# class VisaApplicationsGetSerializer(serializers.ModelSerializer):
#     services = IndividualServiceDetailsSerializer(many=True)
#     email = serializers.SerializerMethodField()
#     mobile_number = serializers.SerializerMethodField()
#
#     class Meta:
#         model = VisaApplications
#         fields = "__all__"
#
#     def get_email(self, obj):
#         # Assuming the related User model has the email field
#         return obj.user.email if obj.user else None
#
#     def get_mobile_number(self, obj):
#         # Assuming the related User model has the mobile_number field
#         return obj.user.mobile_number if obj.user else None
#
# class VisaClientUserListSerializer(serializers.ModelSerializer):
#     services = ServiceDetailsSerializer(many=True)
#     email = serializers.SerializerMethodField()
#     mobile_number = serializers.SerializerMethodField()
#     first_name = serializers.SerializerMethodField()
#     last_name = serializers.SerializerMethodField()
#     user = serializers.SerializerMethodField()
#
#     class Meta:
#         model = VisaApplications
#         fields = "__all__"  # Ensure this includes any fields from `VisaApplications` needed
#
#     def get_email(self, obj):
#         # Assuming the related User model has the email field
#         return obj.user.email if obj.user else None
#
#     def get_mobile_number(self, obj):
#         # Assuming the related User model has the mobile_number field
#         return obj.user.mobile_number if obj.user else None
#
#     def get_first_name(self, obj):
#         # Assuming the related User model has the email field
#         return obj.user.first_name if obj.user else None
#
#     def get_last_name(self, obj):
#         # Assuming the related User model has the mobile_number field
#         return obj.user.last_name if obj.user else None
#
#     def get_user(self, obj):
#         # Assuming the related User model has the mobile_number field
#         return obj.user.id if obj.user else None
#
#
# class ContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Contact
#         fields = "__all__"
#
#     def validate_email(self, value):
#         """ Ensure only one request per email per day """
#         today = now().date()  # Get today's date
#         if Contact.objects.filter(email=value, created_date=today).exists():
#             raise serializers.ValidationError("You can only submit one request per day.")
#         return value
#
#
# class ConsultationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Consultation
#         fields = "__all__"
#
#     def validate_time(self, value):
#         """ Ensure time is stored in HH:MM format only (remove seconds) """
#         return value.replace(second=0)
#
#     def validate(self, data):
#         """ Prevent duplicate bookings for the same date, time slot, and email """
#         email = data.get("email")
#         date = data.get("date")
#         time = data.get("time")
#
#         # Check if the same email has already booked this slot
#         if Consultation.objects.filter(email=email, date=date, time=time).exists():
#             raise serializers.ValidationError(
#                 {"time": "This time slot is already booked. Please select a different slot."}
#             )
#
#         return data
#
