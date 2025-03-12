from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
import boto3
from Tara.settings.default import *
from botocore.exceptions import ClientError
import csv
import pandas as pd
from io import TextIOWrapper
from django.shortcuts import get_object_or_404
from user_management.serializers import *
from django.db import transaction, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
import json
from .helpers import *


def upload_to_s3(pdf_data, bucket_name, object_key):
    try:
        # Save the PDF to an S3 bucket
        s3 = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        response = s3.put_object(Bucket=bucket_name, Key=object_key, Body=pdf_data)
        s3_path = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        return s3_path
    except Exception as e:
        return Response({'error_message': str(e), 'status_cd': 1},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# def generate_presigned_url(s3_key, expiration=3600):
#     """
#     Generate a presigned URL for accessing a private S3 file.
#     """
#     s3 = boto3.client(
#         's3',
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     )
#     try:
#         url = s3.generate_presigned_url(
#             'get_object',
#             Params={'Bucket':AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
#             ExpiresIn=expiration,
#         )
#         return url
#     except Exception as e:
#         raise Exception(f"Error generating presigned URL: {str(e)}")


class PayrollOrgList(APIView):
    """
    List all PayrollOrg instances or create a new PayrollOrg.
    """
    def get(self, request):
        payroll_orgs = PayrollOrg.objects.all()
        serializer = PayrollOrgSerializer(payroll_orgs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        file = request.FILES.get('logo')  # Handle uploaded file (logo)
        bucket_name = S3_BUCKET_NAME
        business_id = data.get('business')
        business_data = data.pop('business_details', None)

        # Fetch business instance
        try:
            business = Business.objects.get(pk=business_id)
        except ObjectDoesNotExist:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update business details if provided
        if business_data:
            if isinstance(business_data, list):  # Ensure we are working with a list
                business_data = business_data[0]  # Extract the first element (string)
            try:
                business_data = json.loads(business_data)  # Convert JSON string to dictionary
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format in business_details"},
                                status=status.HTTP_400_BAD_REQUEST)
            business_serializer = BusinessSerializer(business, data=business_data, partial=True)
            if business_serializer.is_valid():
                business_serializer.save()
            else:
                return Response(business_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle file upload
        if file:
            sanitized_file_name = file.name.replace(" ", "_")
            object_key = f'{business.nameOfBusiness}/business_logo/{sanitized_file_name}'

            try:
                data['logo'] = upload_to_s3(file.read(), bucket_name, object_key)
            except Exception as e:
                return Response({"error": f"File upload failed: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Fetch or create PayrollOrg
        try:
            payroll_org = PayrollOrg.objects.get(business_id=business_id)
            serializer = PayrollOrgSerializer(payroll_org, data=data, partial=True)
        except PayrollOrg.DoesNotExist:
            serializer = PayrollOrgSerializer(data=data)

        # Validate and save PayrollOrg
        if serializer.is_valid():
            payroll_org = serializer.save()
            return Response(PayrollOrgSerializer(payroll_org).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def business_payroll_check(request):
    """
    API to retrieve a business by client ID.
    """
    try:

        client_id = request.query_params.get('user_id')
        business_id = request.query_params.get('business_id')
        if client_id:

            try:
                business = Business.objects.get(client=client_id)  # Using get() instead of filter()
            except Business.DoesNotExist:
                return Response({'error': 'No business found for this client.'}, status=status.HTTP_404_NOT_FOUND)

        if business_id:
            try:
                business = Business.objects.get(id=business_id)  # Using get() instead of filter()
            except Business.DoesNotExist:
                return Response({'error': 'No business found for this client.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize business data
        serializer = BusinessSerializer(business)
        response_data = serializer.data

        # Check if PayrollOrg exists for this business
        organisation_details = PayrollOrg.objects.filter(business=business).exists()

        if organisation_details:
            payroll_org = PayrollOrg.objects.get(business=business.id)

            # payroll_data = PayrollOrgSerializer(payroll_org).data  # Serialize PayrollOrg
            # payroll_data["organisation_address"] = dict(payroll_data.get("organisation_address", {}))

            # Check if all necessary components exist
            all_components = all([
                WorkLocations.objects.filter(payroll=payroll_org.id).exists() or payroll_org.work_location,
                Departments.objects.filter(payroll=payroll_org.id).exists() or payroll_org.department,
                Designation.objects.filter(payroll=payroll_org.id).exists() or payroll_org.designation,
                payroll_org.statutory_component or all([
                    EPF.objects.filter(payroll=payroll_org.id).exists(),
                    ESI.objects.filter(payroll=payroll_org.id).exists(),
                    PT.objects.filter(payroll=payroll_org.id).exists()
                ]),
                payroll_org.salary_component or all([
                    Earnings.objects.filter(payroll=payroll_org.id).exists(),
                    Benefits.objects.filter(payroll=payroll_org.id).exists(),
                    Deduction.objects.filter(payroll=payroll_org.id).exists(),
                    Reimbursement.objects.filter(payroll=payroll_org.id).exists()
                ]),
                payroll_org.salary_template or SalaryTemplate.objects.filter(payroll=payroll_org.id).exists(),
                payroll_org.pay_schedule or PaySchedule.objects.filter(payroll=payroll_org.id).exists(),
                payroll_org.leave_management or False,
                payroll_org.holiday_management or False,
                payroll_org.employee_master or False,
            ])
        else:
            all_components = False  # If PayrollOrg does not exist, setup is incomplete

        # Add payroll setup status to the response
        response_data["payroll_setup"] = all_components

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayrollOrgDetail(APIView):
    """
    Retrieve, update or delete a payroll organization instance.
    """

    def get(self, request, pk):
        try:
            # Fetch PayrollOrg or return 404
            payroll_org = get_object_or_404(PayrollOrg, pk=pk)

            # Fetch associated Business
            business = payroll_org.business

            # Serialize PayrollOrg
            payroll_serializer = PayrollOrgSerializer(payroll_org)

            # Serialize Business
            business_serializer = BusinessSerializer(business)  # Serialize full business data

            # Construct response with full business details
            response_data = payroll_serializer.data  # Get serialized PayrollOrg data
            response_data["business_details"] = business_serializer.data  # Add full Business details

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            payroll_org = PayrollOrg.objects.get(pk=pk)
        except PayrollOrg.DoesNotExist:
            return Response({"error": "PayrollOrg not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        file = request.FILES.get('logo')  # Handle uploaded file (logo)
        bucket_name = S3_BUCKET_NAME

        if file:
            # Replace spaces with underscores in the file name
            sanitized_file_name = file.name.replace(" ", "_")
            business_name = request.data.get('org_name', 'default_org').replace(" ",
                                                                                "_")  # Ensure no spaces in org_name
            object_key = f'{business_name}/business_logo/{sanitized_file_name}'

            try:
                # Upload file to S3 as private
                url = upload_to_s3(file.read(), bucket_name, object_key)  # Read file content for upload
                # Store the S3 URL in the `logo` field
                data['logo'] = url
            except Exception as e:
                return Response(
                    {"error": f"File upload failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Validate and update the serializer
        serializer = PayrollOrgSerializer(payroll_org, data=data, partial=True)
        if serializer.is_valid():
            payroll_org = serializer.save()  # Update the instance directly
            return Response(
                PayrollOrgSerializer(payroll_org).data,
                status=status.HTTP_200_OK
            )

        # Handle validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            payroll_org = PayrollOrg.objects.get(pk=pk)
            payroll_org.delete()
            return Response({"message": "PayrollOrg deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except PayrollOrg.DoesNotExist:
            return Response({"error": "PayrollOrg not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_payroll_org(request, business_id):
    try:
        business = Business.objects.get(pk=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        payroll_org = PayrollOrg.objects.get(business_id=business_id)
    except PayrollOrg.DoesNotExist:
        return Response({"error": "PayrollOrg not found for this business"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    file = request.FILES.get('logo')  # Handle uploaded file (logo)
    bucket_name = S3_BUCKET_NAME

    if file:
        # Sanitize file name
        sanitized_file_name = file.name.replace(" ", "_")
        business_name = request.data.get('org_name', 'default_org').replace(" ", "_")
        object_key = f'{business_name}/business_logo/{sanitized_file_name}'

        try:
            # Upload file to S3
            url = upload_to_s3(file.read(), bucket_name, object_key)
            data['logo'] = url
        except Exception as e:
            return Response({"error": f"File upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Get fields dynamically from serializers
    payroll_org_fields = set(PayrollOrgSerializer().get_fields().keys())
    business_fields = set(BusinessSerializer().get_fields().keys())

    payroll_org_data = {key: value for key, value in data.items() if key in payroll_org_fields}
    business_data = {key: value for key, value in data.items() if key in business_fields}

    # Use a transaction to ensure atomicity
    with transaction.atomic():
        if payroll_org_data:
            payroll_serializer = PayrollOrgSerializer(payroll_org, data=payroll_org_data, partial=True)
            if payroll_serializer.is_valid():
                payroll_serializer.save()
            else:
                return Response(payroll_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if business_data:
            business_serializer = BusinessSerializer(business, data=business_data, partial=True)
            if business_serializer.is_valid():
                business_serializer.save()
            else:
                return Response(business_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Successfully updated"}, status=status.HTTP_200_OK)


class PayrollOrgBusinessDetail(APIView):
    """
    Retrieve a payroll organization instance by its business ID.
    """

    def get(self, request, business_id):
        try:
            payroll_org = PayrollOrg.objects.get(business_id=business_id)
            serializer = PayrollOrgSerializer(payroll_org)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PayrollOrg.DoesNotExist:
            return Response(
                {"error": "Payroll organization not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PayrollOrgBusinessDetailView(APIView):
    def get(self, request, business_id):
        try:
            business = get_object_or_404(Business, id=business_id)
            # Check if PayrollOrg exists
            payroll_org = PayrollOrg.objects.filter(business=business_id).first()
            organisation_details = bool(payroll_org)

            response_data = {
                "business": business.id,
                "organisation_name": business.nameOfBusiness,
                "organisation_address": business.headOffice,
                # Checking existence of related objects
                "organisation_details": organisation_details,
                "payroll_id": payroll_org.id if organisation_details else None,
                "work_locations": WorkLocations.objects.filter(
                    payroll=payroll_org.id).exists() or payroll_org.work_location if organisation_details else False,
                "departments": Departments.objects.filter(payroll=payroll_org.id).exists() or payroll_org.department
                if organisation_details else False,
                "designations": Designation.objects.filter(payroll=payroll_org.id).exists() or payroll_org.designation
                if organisation_details else False,

                # Checking statutory components
                "statutory_component": (
                    payroll_org.statutory_component
                    if payroll_org.statutory_component is True
                    else (
                            EPF.objects.filter(payroll=payroll_org.id).exists()
                            and ESI.objects.filter(payroll=payroll_org.id).exists()
                            and PT.objects.filter(payroll=payroll_org.id).exists()
                    )
                ) if organisation_details else False,

                "salary_component": (
                    payroll_org.salary_component
                    if payroll_org.salary_component is True
                    else (
                            Earnings.objects.filter(payroll=payroll_org.id).exists()
                            and Benefits.objects.filter(payroll=payroll_org.id).exists()
                            and Deduction.objects.filter(payroll=payroll_org.id).exists()
                            and Reimbursement.objects.filter(payroll=payroll_org.id).exists()
                    )
                ) if organisation_details else False,
                "pay_schedule": payroll_org.pay_schedule or PaySchedule.objects.filter(payroll=payroll_org.id).exists()
                if organisation_details else False,
                "leave_and_attendance": (LeaveManagement.objects.filter(payroll=payroll_org.id).exists()) and (
                            HolidayManagement.objects.filter(payroll=payroll_org.id).exists()) if organisation_details
                else False,
                "employee_master": payroll_org.employee_master or False if organisation_details else False,
                "salary_template": payroll_org.salary_template or
                                   SalaryTemplate.objects.filter(payroll=payroll_org.id).exists()
                if organisation_details else False
                }

            return Response(response_data,  status=status.HTTP_200_OK)

        except Business.DoesNotExist:
            return Response({"error": "Business does not exists, Please set up the Business"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# List all WorkLocations
@api_view(['GET'])
def work_location_list(request):
    business_id = request.query_params.get('business_id')
    payroll_id = request.query_params.get('payroll_id')
    try:
        if payroll_id:
            # Retrieve Work Locations for given payroll
            payroll_org = PayrollOrg.objects.get(id=payroll_id)
            business = payroll_org.business  # Fetch business linked to PayrollOrg

            work_locations = WorkLocations.objects.filter(payroll=payroll_org)
            work_location_data = WorkLocationSerializer(work_locations, many=True).data
            return Response(work_location_data, status=status.HTTP_200_OK)

        return Response({"error": "Either business_id or payroll_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    except Business.DoesNotExist:
        return Response({"error": "Invalid Business ID"}, status=status.HTTP_404_NOT_FOUND)

    except PayrollOrg.DoesNotExist:
        return Response({"error": "Invalid Payroll ID"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create a new WorkLocation
@api_view(['POST'])
def work_location_create(request):
    if request.method == 'POST':
        serializer = WorkLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def bulk_work_location_upload(request):
    # Get payroll_id from form data
    payroll_id = request.data.get('payroll_id')
    if not payroll_id:
        return Response({"error": "Payroll ID is required in the form data."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch PayrollOrg based on payroll_id
        payroll_org = PayrollOrg.objects.get(id=payroll_id)
    except PayrollOrg.DoesNotExist:
        return Response({"error": "PayrollOrg not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if file is provided
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check file format (CSV or Excel)
    if file.name.endswith('.csv'):
        try:
            data = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
            records = list(data)
        except Exception as e:
            return Response({"error": f"CSV file reading failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    elif file.name.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
            records = df.to_dict(orient='records')
        except Exception as e:
            return Response({"error": f"Excel file reading failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Unsupported file format. Please upload CSV or Excel."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Validate and Save Records
    errors = []
    for record in records:
        record['payroll'] = payroll_org  # Add payroll to each record manually
        serializer = WorkLocationSerializer(data=record)
        if serializer.is_valid():
            serializer.save()
        else:
            errors.append({"record": record, "errors": serializer.errors})

    if errors:
        return Response({"message": "Partial success", "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

    return Response({"message": "All locations uploaded successfully."}, status=status.HTTP_201_CREATED)


# Retrieve a specific WorkLocation by ID
@api_view(['GET'])
def work_location_detail(request, pk):
    try:
        work_location = WorkLocations.objects.get(pk=pk)
    except WorkLocations.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WorkLocationSerializer(work_location)
        return Response(serializer.data)


# Update a specific WorkLocation by ID
@api_view(['PUT'])
def work_location_update(request, pk):
    try:
        work_location = WorkLocations.objects.get(pk=pk)
    except WorkLocations.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = WorkLocationSerializer(work_location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a specific WorkLocation by ID
@api_view(['DELETE'])
def work_location_delete(request, pk):
    try:
        work_location = WorkLocations.objects.get(pk=pk)
    except WorkLocations.DoesNotExist:
        return Response({"error": "Work location not found"}, status=status.HTTP_404_NOT_FOUND)

    work_location.delete()
    return Response({"message": "Work location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# List and create departments
@api_view(['GET', 'POST'])
def department_list(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')  # Get payroll_id from query parameters

        if payroll_id:
            # Filter departments by payroll_id
            departments = Departments.objects.filter(payroll_id=payroll_id).order_by('-id')
        else:
            # Retrieve all departments if no payroll_id is provided
            departments = Departments.objects.all().order_by('-id')

        serializer = DepartmentsSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = DepartmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def parse_file(file):
    """
    Parse the uploaded file into a list of records.
    Supports CSV and Excel file formats.
    """
    if file.name.endswith('.csv'):
        try:
            data = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
            return list(data), None
        except Exception as e:
            return None, f"CSV file reading failed: {str(e)}"

    elif file.name.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
            return df.to_dict(orient='records'), None
        except Exception as e:
            return None, f"Excel file reading failed: {str(e)}"

    return None, "Unsupported file format. Please upload CSV or Excel."


@api_view(['POST'])
def bulk_department_upload(request):
    # Validate payroll_id
    payroll_id = request.data.get('payroll_id')
    if not payroll_id:
        return Response({"error": "Payroll ID is required in the form data."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch PayrollOrg
    try:
        payroll_org = PayrollOrg.objects.get(id=payroll_id)
    except PayrollOrg.DoesNotExist:
        return Response({"error": "PayrollOrg not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check for file in request
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Parse file based on format (CSV or Excel)
    records, parse_error = parse_file(file)
    if parse_error:
        return Response({"error": parse_error}, status=status.HTTP_400_BAD_REQUEST)

    # Validate and save each record
    errors = []
    for record in records:
        record['payroll'] = payroll_org  # Assign payroll org to each record
        serializer = DepartmentsSerializer(data=record)
        if serializer.is_valid():
            serializer.save()
        else:
            errors.append({"record": record, "errors": serializer.errors})

    if errors:
        return Response({"message": "Partial success", "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

    return Response({"message": "All departments uploaded successfully."}, status=status.HTTP_201_CREATED)


# Retrieve, update or delete a specific department
@api_view(['GET', 'PUT', 'DELETE'])
def department_detail(request, pk):
    try:
        department = Departments.objects.get(pk=pk)
    except Departments.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DepartmentsSerializer(department)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DepartmentsSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# List and create Designations
@api_view(['GET', 'POST'])
def designation_list(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')  # Get payroll_id from query parameters

        if payroll_id:
            # Filter designations by payroll_id
            designations = Designation.objects.filter(payroll_id=payroll_id).order_by('-id')
        else:
            # Retrieve all designations if no payroll_id is provided
            designations = Designation.objects.all().order_by('-id')
        serializer = DesignationSerializer(designations, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DesignationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, update, or delete a specific Designation
@api_view(['GET', 'PUT', 'DELETE'])
def designation_detail(request, pk):
    try:
        designation = Designation.objects.get(pk=pk)
    except Designation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DesignationSerializer(designation)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DesignationSerializer(designation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        designation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def bulk_designation_upload(request):
    # Validate payroll_id
    payroll_id = request.data.get('payroll_id')
    if not payroll_id:
        return Response({"error": "Payroll ID is required in the form data."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch PayrollOrg
    try:
        payroll_org = PayrollOrg.objects.get(id=payroll_id)
    except PayrollOrg.DoesNotExist:
        return Response({"error": "PayrollOrg not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check for file in request
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Parse file based on format (CSV or Excel)
    records, parse_error = parse_file(file)
    if parse_error:
        return Response({"error": parse_error}, status=status.HTTP_400_BAD_REQUEST)

    # Validate and save each record
    errors = []
    for record in records:
        record['payroll'] = payroll_org  # Assign payroll org to each record
        serializer = DesignationSerializer(data=record)
        if serializer.is_valid():
            serializer.save()
        else:
            errors.append({"record": record, "errors": serializer.errors})

    if errors:
        return Response({"message": "Partial success", "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

    return Response({"message": "All departments uploaded successfully."}, status=status.HTTP_201_CREATED)


# List and create EPF details
@api_view(['GET', 'POST'])
def epf_list(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')  # Get payroll_id from query parameters

        if payroll_id:
            # Since payroll is a OneToOneField, there will be at most one EPF record for a given payroll_id
            try:
                epf_details = EPF.objects.get(payroll=payroll_id)  # Fetch EPF details for the specific payroll
                serializer = EPFSerializer(epf_details)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except EPF.DoesNotExist:
                return Response({"error": "EPF details not found for the given payroll ID."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all EPF details if no payroll_id is provided
            epf_details = EPF.objects.all()
            serializer = EPFSerializer(epf_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EPFSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Ensure there is no existing EPF record for the given payroll_id
                payroll_id = serializer.validated_data.get('payroll').id
                if EPF.objects.filter(payroll_id=payroll_id).exists():
                    return Response({"error": "EPF details already exist for this payroll ID."}, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, update, or delete specific EPF details
@api_view(['GET', 'PUT', 'DELETE'])
def epf_detail(request, pk):
    try:
        epf = EPF.objects.get(pk=pk)
    except EPF.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EPFSerializer(epf)
        return Response(serializer.data,  status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = EPFSerializer(epf, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        epf.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# List and create ESI details
@api_view(['GET', 'POST'])
def esi_list(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')  # Get payroll_id from query parameters

        if payroll_id:
            # Since payroll is a OneToOneField, there will be at most one ESI record for a given payroll_id
            try:
                esi_details = ESI.objects.get(payroll_id=payroll_id)  # Fetch ESI details for the specific payroll
                serializer = ESISerializer(esi_details)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ESI.DoesNotExist:
                return Response({"error": "ESI details not found for the given payroll ID."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all ESI details if no payroll_id is provided
            esi_details = ESI.objects.all()
            serializer = ESISerializer(esi_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ESISerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Ensure there is no existing ESI record for the given payroll_id
                payroll_id = serializer.validated_data.get('payroll').id
                if ESI.objects.filter(payroll_id=payroll_id).exists():
                    return Response({"error": "ESI details already exist for this payroll ID."}, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, update, or delete specific ESI details
@api_view(['GET', 'PUT', 'DELETE'])
def esi_detail(request, pk):
    try:
        esi = ESI.objects.get(pk=pk)
    except ESI.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ESISerializer(esi)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ESISerializer(esi, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        esi.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def pt_list(request):
    """
    List PF records or create a new one, based on payroll_id.
    """
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')

        if not payroll_id:
            return Response({"error": "payroll_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        pt_instances = PT.objects.filter(payroll_id=payroll_id)

        if not pt_instances.exists():
            # Fetch work locations linked to this payroll_id
            work_location_instances = WorkLocations.objects.filter(payroll_id=payroll_id)

            if not work_location_instances.exists():
                return Response({"error": "No PT records or work locations found for the given payroll ID."},
                                status=status.HTTP_404_NOT_FOUND)

            # Create PT objects dynamically
            pt_objects = []
            for wl in work_location_instances:
                pt = PT(payroll_id=payroll_id, work_location=wl)
                pt.save()  # Automatically assigns the slab in the model's `save()` method
                pt_objects.append(pt)

            # Fetch newly created PT objects
            pt_instances = PT.objects.filter(payroll_id=payroll_id)

        serializer = PTSerializerRetrieval(pt_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PTSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def pt_detail(request, pk):
    """
    Retrieve, update or delete a PF record.
    """
    try:
        pt_instance = PT.objects.get(pk=pk)
    except PT.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PTSerializerRetrieval(pt_instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PTSerializer(pt_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pt_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def earnings_list(request):
    """
    List all Earnings records, or create a new one.
    """
    if request.method == 'GET':
        try:
            payroll_id = request.query_params.get('payroll_id')

            if not payroll_id:
                return Response({"error": "payroll_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                payroll_instance = PayrollOrg.objects.get(id=payroll_id)  # Fetch PayrollOrg instance
            except PayrollOrg.DoesNotExist:
                return Response({"error": "Invalid payroll_id"}, status=status.HTTP_400_BAD_REQUEST)

            # Filter earnings by payroll instance
            earnings = Earnings.objects.filter(payroll=payroll_instance)
            if not earnings.exists():
                created_earnings = []  # Track created earnings to manually delete on error
                try:
                    with transaction.atomic():  # Ensures all-or-nothing behavior
                        for earning_data in default_earnings:
                            earning_data['payroll'] = payroll_instance.id  # Assign ID

                            # Validate and save using serializer
                            serializer = EarningsSerializer(data=earning_data)
                            if serializer.is_valid(raise_exception=True):
                                created_earning = serializer.save()
                                created_earnings.append(created_earning)  # Track created object
                            else:
                                raise DatabaseError("Earning data is invalid, transaction will be rolled back.")
                except (ValidationError, DatabaseError) as e:
                    # Handle exceptions gracefully and rollback
                    # Manually delete created earnings if an error occurs
                    for earning in created_earnings:
                        earning.delete()
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    # Clean up if something unexpected happens
                    for earning in created_earnings:
                        earning.delete()
                    return Response({"error": f"Unexpected error occurred: {str(e)}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # If everything works, get the earnings
                earnings = Earnings.objects.filter(payroll=payroll_instance)

            serializer = EarningsSerializerRetrieval(earnings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        data = request.data.copy()
        payroll_id = data.get('payroll')
        if not payroll_id:
            return Response({"error": "payroll_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EarningsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def earnings_detail(request, pk):
    """
    Retrieve, update, or delete an Earnings record.
    """
    try:
        earnings = Earnings.objects.get(pk=pk)
    except Earnings.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EarningsSerializer(earnings)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EarningsSerializer(earnings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        earnings.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def benefits_list_create(request):
    """
    Handles GET (list) and POST (create) for Benefits.
    - GET: Returns a list of all Benefits, optionally filtered by `payroll` or `payslip_name`.
    - POST: Creates a new Benefit entry.
    """
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll')
        payslip_name = request.query_params.get('payslip_name')

        # Filter Benefits based on query parameters if provided
        benefits = Benefits.objects.all()
        if payroll_id:
            benefits = benefits.filter(payroll_id=payroll_id)
        if payslip_name:
            benefits = benefits.filter(payslip_name=payslip_name)

        serializer = BenefitsSerializer(benefits, many=True)
        return Response({"data": serializer.data, "message": "Benefits retrieved successfully."}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = BenefitsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Benefit created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def benefits_detail_update_delete(request, benefit_id):
    """
    Handles GET, PUT, and DELETE for a single Benefit based on its ID.
    - GET: Retrieves details of a specific Benefit.
    - PUT: Updates a specific Benefit.
    - DELETE: Deletes a specific Benefit.
    """
    try:
        benefit = Benefits.objects.get(id=benefit_id)
    except Benefits.DoesNotExist:
        return Response({"error": "Benefit not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BenefitsSerializer(benefit)
        return Response({"data": serializer.data, "message": "Benefit retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BenefitsSerializer(benefit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Benefit updated successfully."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        benefit.delete()
        return Response({"message": "Benefit deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def deduction_list_create(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')  # Get payroll_id from query parameters

        if payroll_id:
            # Filter designations by payroll_id
            deductions = Deduction.objects.filter(payroll_id=payroll_id)
        else:
            # Retrieve all designations if no payroll_id is provided
            deductions = Deduction.objects.all()
        serializer = DeductionSerializer(deductions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = DeductionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def deduction_detail(request, id):
    try:
        deduction = Deduction.objects.get(id=id)
    except Deduction.DoesNotExist:
        return Response({"error": "Deduction not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DeductionSerializer(deduction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = DeductionSerializer(deduction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        deduction.delete()
        return Response({"message": "Deduction deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def reimbursement_list_create(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')  # Get payroll_id from query parameters

        if payroll_id:
            # Filter reimbursements by payroll_id
            reimbursements = Reimbursement.objects.filter(payroll_id=payroll_id)
        else:
            # Retrieve all reimbursements if no payroll_id is provided
            reimbursements = Reimbursement.objects.all()
        serializer = ReimbursementSerializer(reimbursements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = ReimbursementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def reimbursement_detail(request, id):
    try:
        reimbursement = Reimbursement.objects.get(id=id)
    except Reimbursement.DoesNotExist:
        return Response({"error": "Reimbursement not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReimbursementSerializer(reimbursement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = ReimbursementSerializer(reimbursement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        reimbursement.delete()
        return Response({"message": "Reimbursement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def salary_template_list_create(request):
    """
    Handles GET (list) and POST (create) for Salary Templates.
    - GET: Returns a list of all Salary Templates, optionally filtered by `payroll` or `template_name`.
    - POST: Creates a new Salary Template entry.
    """
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')
        template_name = request.query_params.get('template_name')

        if payroll_id:
            salary_templates = SalaryTemplate.objects.filter(payroll_id=payroll_id)

        serializer = SalaryTemplateSerializer(salary_templates, many=True)
        return Response({"data": serializer.data, "message": "Salary Templates retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SalaryTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Salary Template created successfully."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def salary_template_detail_update_delete(request, template_id):
    """
    Handles GET, PUT, and DELETE for a single Salary Template based on its ID.
    - GET: Retrieves details of a specific Salary Template.
    - PUT: Updates a specific Salary Template.
    - DELETE: Deletes a specific Salary Template.
    """
    try:
        salary_template = SalaryTemplate.objects.get(id=template_id)
    except SalaryTemplate.DoesNotExist:
        return Response({"error": "Salary Template not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SalaryTemplateSerializer(salary_template)
        return Response({"data": serializer.data, "message": "Salary Template retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SalaryTemplateSerializer(salary_template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Salary Template updated successfully."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        salary_template.delete()
        return Response({"message": "Salary Template deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def pay_schedule_list_create(request):
    """
    Handles GET (list) and POST (create) for Pay Schedules.
    - GET: Returns a list of all Pay Schedules, optionally filtered by `payroll`.
    - POST: Creates a new Pay Schedule entry ensuring at least two days are selected.
    """
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')

        if payroll_id:
            try:
                pay_schedule = PaySchedule.objects.get(payroll_id=payroll_id)
                serializer = PayScheduleSerializer(pay_schedule)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(
                    {"error": "No Pay Schedule found for the provided payroll_id."},
                    status=status.HTTP_404_NOT_FOUND
                )

        pay_schedules = PaySchedule.objects.all()
        serializer = PayScheduleSerializer(pay_schedules, many=True)
        return Response(
            {"data": serializer.data, "message": "Pay Schedules retrieved successfully."},
            status=status.HTTP_200_OK
        )

    elif request.method == 'POST':
        serializer = PayScheduleSerializer(data=request.data)
        if serializer.is_valid():
            days_selected = sum([
                serializer.validated_data.get(day, False) for day in [
                    'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'second_saturday',
                    'fourth_saturday'
                ]
            ])
            if days_selected < 2:
                return Response({"error": "At least two days must be selected."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"data": serializer.data, "message": "Pay Schedule created successfully."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def pay_schedule_detail_update_delete(request, schedule_id):
    """
    Handles GET, PUT, and DELETE for a single Pay Schedule based on its ID.
    - GET: Retrieves details of a specific Pay Schedule.
    - PUT: Updates a specific Pay Schedule ensuring at least two days are selected.
    - DELETE: Deletes a specific Pay Schedule.
    """
    try:
        pay_schedule = PaySchedule.objects.get(id=schedule_id)
    except PaySchedule.DoesNotExist:
        return Response({"error": "Pay Schedule not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PayScheduleSerializer(pay_schedule)
        return Response({"data": serializer.data, "message": "Pay Schedule retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = PayScheduleSerializer(pay_schedule, data=request.data)
        if serializer.is_valid():
            days_selected = sum([
                serializer.validated_data.get(day, False) for day in [
                    'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'second_saturday',
                    'fourth_saturday'
                ]
            ])
            if days_selected < 2:
                return Response({"error": "At least two days must be selected."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"data": serializer.data, "message": "Pay Schedule updated successfully."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pay_schedule.delete()
        return Response({"message": "Pay Schedule deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def leave_management_list_create(request):
    """
    API for listing and creating Leave Management records.
    - GET: Retrieves all leave policies.
    - POST: Creates a new leave policy.
    """
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')
        leaves = LeaveManagement.objects.all()
        if payroll_id:
            leaves = leaves.filter(payroll_id=payroll_id)

        serializer = LeaveManagementSerializer(leaves, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = LeaveManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Leave Management record created successfully."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def leave_management_detail_update_delete(request, leave_id):
    """
    API for retrieving, updating, and deleting a single Leave Management record.
    """
    try:
        leave = LeaveManagement.objects.get(id=leave_id)
    except LeaveManagement.DoesNotExist:
        return Response({"error": "Leave Management record not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LeaveManagementSerializer(leave)
        return Response({"data": serializer.data, "message": "Leave Management record retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = LeaveManagementSerializer(leave, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        leave.delete()
        return Response({"message": "Leave Management record deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def holiday_management_list_create(request):
    """
    API for listing and creating Holiday Management records.
    - GET: Retrieves all holidays.
    - POST: Creates a new holiday entry.
    """
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')
        holidays = HolidayManagement.objects.all()
        if payroll_id:
            holidays = holidays.filter(payroll_id=payroll_id)

        serializer = HolidayManagementSerializer(holidays, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = HolidayManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def holiday_management_filtered_list(request):
    """
    API for retrieving Holiday Management records based on payroll_id, financial_year, and applicable_for.
    - GET: Retrieves holidays filtered by provided query parameters.
    """
    filters = {}

    payroll_id = request.query_params.get('payroll_id')
    financial_year = request.query_params.get('financial_year')
    applicable_for = request.query_params.get('applicable_for')

    if payroll_id:
        filters['payroll_id'] = payroll_id
    if financial_year:
        filters['financial_year'] = financial_year
    if applicable_for:
        filters['applicable_for'] = applicable_for

    holidays = HolidayManagement.objects.filter(**filters)  # Apply filters directly

    serializer = HolidayManagementSerializer(holidays, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def holiday_management_detail_update_delete(request, holiday_id):
    """
    API for retrieving, updating, and deleting a single Holiday Management record.
    """
    try:
        holiday = HolidayManagement.objects.get(id=holiday_id)
    except HolidayManagement.DoesNotExist:
        return Response({"error": "Holiday Management record not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = HolidayManagementSerializer(holiday)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = HolidayManagementSerializer(holiday, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        holiday.delete()
        return Response({"message": "Holiday Management record deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def employee_list(request):
    if request.method == 'GET':
        payroll_id = request.query_params.get('payroll_id')
        if payroll_id:
            employees = EmployeeManagement.objects.filter(payroll_id=payroll_id)
        else:
            employees = EmployeeManagement.objects.all()
        serializer = EmployeeManagementSerializer(employees, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EmployeeManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def employee_detail(request, pk):
    employee = get_object_or_404(EmployeeManagement, pk=pk)

    if request.method == 'GET':
        serializer = EmployeeManagementSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = EmployeeManagementSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        employee.delete()
        return Response({"message": "Employee data Removed Successfully."},
                        status=status.HTTP_204_NO_CONTENT)


# Employee Salary Views
@api_view(['GET', 'POST'])
def employee_salary_list(request):
    if request.method == 'GET':
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            salaries = EmployeeSalaryDetails.objects.filter(employee=employee_id)
        else:
            salaries = EmployeeSalaryDetails.objects.all()
        serializer = EmployeeSalaryDetailsSerializer(salaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EmployeeSalaryDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def employee_salary_detail(request, pk):
    """
    Handles GET, PUT, and DELETE for a single Employee Salary based on its ID.
    - GET: Retrieves details of a specific Employee Salary.
    - PUT: Updates a specific Employee Salary.
    - DELETE: Deletes a specific Employee Salary.
    """
    employee_salary_details = get_object_or_404(EmployeeSalaryDetails, pk=pk)

    if request.method == 'GET':
        serializer = EmployeeSalaryDetailsSerializer(employee_salary_details)
        return Response(
            {"data": serializer.data, "message": "Salary details retrieved successfully."},
            status=status.HTTP_200_OK
        )

    elif request.method == 'PUT':
        serializer = EmployeeSalaryDetailsSerializer(employee_salary_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Salary details updated successfully."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"errors": serializer.errors, "message": "Validation failed."},
            status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'DELETE':
        employee_salary_details.delete()
        return Response(
            {"message": "Salary details deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    return Response(
        {"error": "Invalid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


# Employee Personal Details Views
@api_view(['GET', 'POST'])
def employee_personal_list(request):
    if request.method == 'GET':
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            personal_details = EmployeePersonalDetails.objects.filter(employee=employee_id)
        else:
            personal_details = EmployeePersonalDetails.objects.all()
        serializer = EmployeePersonalDetailsSerializer(personal_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EmployeePersonalDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def employee_personal_detail(request, pk):
    personal_detail = get_object_or_404(EmployeePersonalDetails, pk=pk)

    if request.method == 'GET':  # Retrieve personal details
        serializer = EmployeePersonalDetailsSerializer(personal_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':  # Update personal details
        serializer = EmployeePersonalDetailsSerializer(personal_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':  # Delete personal details
        personal_detail.delete()
        return Response({"message": "Employee Personal details deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def employee_bank_list(request):
    """
    Handles listing all employee bank details and creating a new entry.
    """
    if request.method == 'GET':
        bank_details = EmployeeBankDetails.objects.all()
        serializer = EmployeeBankDetailsSerializer(bank_details, many=True)
        return Response({"data": serializer.data, "message": "Bank details retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EmployeeBankDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Bank details added successfully."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def employee_bank_detail(request, pk):
    """
    Handles retrieving, updating, and deleting an employee bank detail by ID.
    """
    bank_detail = get_object_or_404(EmployeeBankDetails, pk=pk)

    if request.method == 'GET':
        serializer = EmployeeBankDetailsSerializer(bank_detail)
        return Response({"data": serializer.data, "message": "Bank detail retrieved successfully."},
                        status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = EmployeeBankDetailsSerializer(bank_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Bank details updated successfully."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        bank_detail.delete()
        return Response({"message": "Bank detail deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)



