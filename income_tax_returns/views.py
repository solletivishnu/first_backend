from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
import json
from .helpers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes


def handle_dynamic_tasks(personal_info_instance):
    service_request = personal_info_instance.service_request
    service_type = personal_info_instance.service_type
    client = service_request.user
    assignee = personal_info_instance.assignee
    reviewer = personal_info_instance.reviewer

    def create_task_if_not_exists(category_name):
        exists = ServiceTask.objects.filter(
            service_request=service_request,
            service_type=service_type,
            category_name=category_name
        ).exists()
        if not exists:
            ServiceTask.objects.create(
                service_request=service_request,
                service_type=service_type,
                category_name=category_name,
                client=client,
                assignee=assignee,
                reviewer=reviewer,
                status="in progress",
                priority="medium"
            )

    # Salary Income-related
    if personal_info_instance.salary_income == 'yes':
        create_task_if_not_exists("Salary Income")
        create_task_if_not_exists("NRI Employee Salary")  # Assumes NRI if flagged separately

    # House Property Income
    if personal_info_instance.house_property_income == 'yes':
        create_task_if_not_exists("House Property Income")

    # Capital Gains Income
    if personal_info_instance.capital_gains == 'yes':
        create_task_if_not_exists("Capital Gains Applicable Details")
        create_task_if_not_exists("Capital Gains Equity Mutual Fund")
        create_task_if_not_exists("Other Capital Gains")

    # Business Income
    if personal_info_instance.business_income == 'yes':
        create_task_if_not_exists("Business Income")

    # Other Income (subcategories)
    if personal_info_instance.other_income == 'yes':
        create_task_if_not_exists("Interest Income")
        create_task_if_not_exists("Dividend Income")
        create_task_if_not_exists("Gift Income")
        create_task_if_not_exists("Family Pension Income")
        create_task_if_not_exists("Foreign Income")
        create_task_if_not_exists("Winning Income")

    # Agriculture Income
    if personal_info_instance.agriculture_income == 'yes':
        create_task_if_not_exists("Agriculture Income")


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personal_information_list(request):
    if request.method == 'GET':
        records = PersonalInformation.objects.all()
        serializer = PersonalInformationSerializer(records, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PersonalInformationSerializer(data=request.data)
        if serializer.is_valid():
            personal_info = serializer.save()
            handle_dynamic_tasks(personal_info)
            return Response(PersonalInformationSerializer(personal_info).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personal_information_detail(request, pk):
    try:
        record = PersonalInformation.objects.get(pk=pk)
    except PersonalInformation.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PersonalInformationSerializer(record)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PersonalInformationSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            personal_info = serializer.save()
            handle_dynamic_tasks(personal_info)
            return Response(PersonalInformationSerializer(personal_info).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personal_information_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = PersonalInformation.objects.get(service_request_id=service_request_id)
        else:
            instance = PersonalInformation.objects.get(service_task_id=service_task_id)
    except PersonalInformation.DoesNotExist:
        return Response({"error": "No matching BusinessLocationProofs found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PersonalInformationSerializer(instance)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_list(request):
    if request.method == 'GET':
        records = ReviewFilingCertificate.objects.all()
        serializer = ReviewFilingCertificateSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ReviewFilingCertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_detail(request, pk):
    try:
        record = ReviewFilingCertificate.objects.get(pk=pk)
    except ReviewFilingCertificate.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewFilingCertificateSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ReviewFilingCertificateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_review_filing_certificate(request):
    """
    Retrieve ReviewFilingCertificate based on either service_request_id or service_task_id.
    """
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = ReviewFilingCertificate.objects.get(service_request_id=service_request_id)
        else:
            instance = ReviewFilingCertificate.objects.get(service_task_id=service_task_id)
    except ReviewFilingCertificate.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewFilingCertificateSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def service_request_tasks_views(request):
    try:
        service_request_id = request.query_params.get('service_request_id')
        service_request = ServiceRequest.objects.get(id=service_request_id)
        tasks = ServiceTask.objects.filter(service_request=service_request)
        serializer = ServiceTaskWithDataSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ServiceRequest.DoesNotExist:
        return Response(
            {'error': 'Service request not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


TASK_MODEL_SERIALIZER_MAP = {
    "Personal Information": (PersonalInformation, PersonalInformationSerializer, False),
    "Tax Paid Details": (TaxPaidDetails, TaxPaidDetailsSerializer, False),
    "Deductions": (Deductions, DeductionsSerializer, False),
    "Review Filing Certificate": (ReviewFilingCertificate, ReviewFilingCertificateSerializer, False),

    # Multiple entries expected
    "Other Income": (OtherIncomeDetails, OtherIncomeDetailsSerializer, True),
    "Gift Income": (GiftIncomeDetails, GiftIncomeDetailsSerializer, True),
    "Foreign Income": (ForeignIncome, ForeignIncomeSerializer, True),
    "Dividend Income": (DividendIncome, DividendIncomeSerializer, True),
    "Interest Income": (InterestIncome, InterestIncomeSerializer, True),
    "Salary Income": (SalaryIncome, SalaryIncomeSerializer, True),
    "NRI Employee Salary": (NRIEmployeeSalaryDetails, NRIEmployeeSalaryDetailsSerializer, True),
    "House Property Income": (HousePropertyIncomeDetails, HousePropertyIncomeDetailsSerializer, True),
    "Family Pension Income": (FamilyPensionIncome, FamilyPensionIncomeSerializer, True),
    "Winning Income": (WinningIncome, WinningIncomeSerializer, True),
    "Agriculture Income": (AgricultureIncome, AgricultureIncomeSerializer, True),
    "Capital Gains Applicable Details": (CapitalGainsApplicableDetails, CapitalGainsApplicableDetailsSerializer, False),
    "Capital Gains Equity Mutual Fund": (CapitalGainsEquityMutualFund, CapitalGainsEquityMutualFundSerializer, False),
    "Other Capital Gains": (OtherCapitalGains, OtherCapitalGainsSerializer, True),
    "Business Income": (BusinessProfessionalIncome, BusinessProfessionalIncomeSerializer, True)
}


@api_view(['GET'])
def get_service_request_full_data(request, service_request_id):
    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'ServiceRequest not found'}, status=status.HTTP_404_NOT_FOUND)

    tasks = service_request.service_tasks.all()
    full_data = {}

    for task in tasks:
        category_name = task.category_name.strip()
        config = TASK_MODEL_SERIALIZER_MAP.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assignee": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }

        if config:
            model_class, serializer_class, is_multiple = config

            queryset = model_class.objects.filter(
                service_request=service_request,
                service_task=task
            )

            if queryset.exists():
                task_info["data"] = (
                    serializer_class(queryset, many=True).data if is_multiple
                    else serializer_class(queryset.first()).data
                )
            else:
                task_info["data"] = [] if is_multiple else None
        else:
            task_info["data"] = "No model/serializer mapping defined"

        full_data[category_name] = task_info

    return Response({
        "service_request": service_request.id,
        "client": service_request.user.id,
        "tasks_data": full_data
    })


CATEGORY_TASK_MAP = {
    "personal_info": ["Personal Information", "Tax Paid Details"],
    "income_details": [
        "Other Income", "Gift Income", "Foreign Income", "Dividend Income",
        "Interest Income", "Salary Income", "NRI Employee Salary",
        "House Property Income", "Family Pension Income", "Winning Income", "Agriculture Income",
        "Capital Gains Applicable Details", "Capital Gains Equity Mutual Fund", "Other Capital Gains", "Business Income"
    ],
    "deductions": ["Deductions"],
    "review": ["Review Filing Certificate"]
}


@api_view(['GET'])
def get_service_request_section_data(request):
    service_request_id = request.query_params.get('service_request_id')
    section_key = request.query_params.get('section')  # e.g. "income_details", "personal_info"
    income_subtype = request.query_params.get('income_type')  # e.g. "Salary Income"

    if not service_request_id or not section_key:
        return Response({"error": "Missing service_request_id or section"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'ServiceRequest not found'}, status=status.HTTP_404_NOT_FOUND)

    allowed_categories = CATEGORY_TASK_MAP.get(section_key)

    if not allowed_categories:
        return Response({"error": "Invalid section key"}, status=status.HTTP_400_BAD_REQUEST)

    # If income_type is explicitly specified, fetch tasks only under that category
    if section_key == "income_details" and income_subtype:
        allowed_categories = [income_subtype]
        tasks = service_request.service_tasks.filter(category_name__in=allowed_categories)
        section_data = {}

        for task in tasks:
            category_name = task.category_name.strip()
            config = TASK_MODEL_SERIALIZER_MAP.get(category_name)

            task_info = {
                "task_id": task.id,
                "category_name": category_name,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "assignee": task.assignee.id if task.assignee else None,
                "reviewer": task.reviewer.id if task.reviewer else None,
                "data": None
            }

            if config:
                model_class, serializer_class, is_multiple = config

                queryset = model_class.objects.filter(
                    service_request=service_request,
                    service_task=task
                )

                task_info["data"] = (
                    serializer_class(queryset, many=True).data if is_multiple
                    else serializer_class(queryset.first()).data if queryset.exists()
                    else ([] if is_multiple else None)
                )
            else:
                task_info["data"] = "No model/serializer mapping defined"

            section_data[category_name] = task_info

        return Response({
            "service_request": service_request.id,
            "client": service_request.user.id,
            "section_key": section_key,
            "tasks_data": section_data
        }, status=status.HTTP_200_OK)

    # ---- REGROUPING for income_details ----
    if section_key == "income_details":
        subgroup_map = {
            "salary_income": {"Salary Income", "NRI Employee Salary", "Other Income"},
            "house_property_income": {"House Property Income"},
            "capital_gains": {"Capital Gains Applicable Details", "Capital Gains Equity Mutual Fund", "Other Capital Gains"},
            "agriculture_income": {"Agriculture Income"},
            "business_income": {"Business Income"},
            "other_income": set(allowed_categories) - {
                "Salary Income", "NRI Employee Salary", "Other Income",
                "House Property Income",
                "Capital Gains Applicable Details", "Capital Gains Equity Mutual Fund", "Other Capital Gains",
                "Agriculture Income"
            }
        }

        tasks = service_request.service_tasks.filter(category_name__in=allowed_categories)

        grouped_data = {
            "salary_income": [],
            "house_property_income": [],
            "capital_gains": [],
            "agriculture_income": [],
            "other_income": [],
            "business_income": []
        }

        for task in tasks:
            category_name = task.category_name.strip()
            config = TASK_MODEL_SERIALIZER_MAP.get(category_name)

            task_info = {
                "task_id": task.id,
                "category_name": category_name,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "assignee": task.assignee.id if task.assignee else None,
                "reviewer": task.reviewer.id if task.reviewer else None,
                "data": None
            }

            if config:
                model_class, serializer_class, is_multiple = config

                queryset = model_class.objects.filter(
                    service_request=service_request,
                    service_task=task
                )

                task_info["data"] = (
                    serializer_class(queryset, many=True).data if is_multiple
                    else serializer_class(queryset.first()).data if queryset.exists()
                    else ([] if is_multiple else None)
                )
            else:
                task_info["data"] = "No model/serializer mapping defined"

            # Assign to appropriate group
            for group_key, category_set in subgroup_map.items():
                if category_name in category_set:
                    grouped_data[group_key].append(task_info)
                    break
        # Filter out empty groups
        filtered_grouped_data = {
            key: value for key, value in grouped_data.items() if value  # only keep non-empty lists
        }

        return Response({
            "service_request": service_request.id,
            "client": service_request.user.id,
            "section_key": section_key,
            "tasks_data": filtered_grouped_data
        }, status=status.HTTP_200_OK)

    # ---- END REGROUPING ----
    # Fallback for non-income section (personal_info, deductions, review)
    tasks = service_request.service_tasks.filter(category_name__in=allowed_categories)

    section_data = {}

    for task in tasks:
        category_name = task.category_name.strip()
        config = TASK_MODEL_SERIALIZER_MAP.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assignee": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }

        if config:
            model_class, serializer_class, is_multiple = config

            queryset = model_class.objects.filter(
                service_request=service_request,
                service_task=task
            )

            task_info["data"] = (
                serializer_class(queryset, many=True).data if is_multiple
                else serializer_class(queryset.first()).data if queryset.exists()
                else ([] if is_multiple else None)
            )
        else:
            task_info["data"] = "No model/serializer mapping defined"

        section_data[category_name] = task_info

    return Response({
        "service_request": service_request.id,
        "client": service_request.user.id,
        "section_key": section_key,
        "tasks_data": section_data
    }, status=status.HTTP_200_OK)



