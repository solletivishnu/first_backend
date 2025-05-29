from rest_framework import serializers
from .models import *
from servicetasks.models import ServiceTask


class PersonalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInformation
        fields = '__all__'


class TaxPaidDetailsFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPaidDetailsFile
        fields = '__all__'


# class TaxPaidDetailsSerializer(serializers.ModelSerializer):
#     tax_paid_documents = TaxPaidDetailsFileSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = TaxPaidDetails
#         fields = '__all__'


class TaxPaidDetailsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = TaxPaidDetails
        fields = '__all__'  # or list the fields explicitly
        depth = 1  # optional, if you want nested object fields expanded

    def get_documents(self, obj):
        grouped = {}
        for doc_type in ['26AS', 'AIS', 'AdvanceTax']:
            files = obj.tax_paid_documents.filter(document_type=doc_type)
            grouped[doc_type] = {
                "count": files.count(),
                "files": [
                    {
                        "id": f.id,
                        "url": f.file.url if f.file else None,
                        "uploaded_at": f.uploaded_at
                    }
                    for f in files
                ]
            }
        return grouped


class SalaryDocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryDocumentFile
        fields = '__all__'


class SalaryIncomeSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = SalaryIncome
        fields = '__all__'

    def get_documents(self, obj):
        doc_types = ['PAYSLIP', 'FORM_16', 'BANK_STATEMENT']  # Adjust as per your types
        grouped = {}
        for doc_type in doc_types:
            files = obj.documents.filter(document_type=doc_type)
            grouped[doc_type] = {
                "count": files.count(),
                "files": [
                    {
                        "id": f.id,
                        "url": f.file.url if f.file else None,
                        "uploaded_at": f.uploaded_at
                    }
                    for f in files
                ]
            }
        return grouped


class OtherIncomeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherIncomeDetails
        fields = '__all__'


class ForeignEmployeeSalaryDetailsFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForeignEmployeeSalaryDetailsFiles
        fields = '__all__'


class NRIEmployeeSalaryDetailsSerializer(serializers.ModelSerializer):
    foreigner_documents = serializers.SerializerMethodField()
    employment_history = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = NRIEmployeeSalaryDetails
        fields = '__all__'

    def get_foreigner_documents(self, obj):
        doc_types = ['Salary Slip', 'TAX PAID CERTIFICATE BOARD', 'Bank Statement']  # Adjust these as per your document_type choices
        grouped = {}
        for doc_type in doc_types:
            files = obj.foreigner_documents.filter(document_type=doc_type)
            grouped[doc_type] = {
                "count": files.count(),
                "files": [
                    {
                        "id": f.id,
                        "url": f.file.url if f.file else None,
                        "uploaded_at": f.uploaded_at
                    }
                    for f in files
                ]
            }
        return grouped


class HousePropertyIncomeDetailsSerializer(serializers.ModelSerializer):
    property_address = serializers.JSONField(required=False, allow_null=True)
    class Meta:
        model = HousePropertyIncomeDetails
        fields = '__all__'


class InterestIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestIncomeDocument
        fields = '__all__'


class InterestIncomeSerializer(serializers.ModelSerializer):
    documents = InterestIncomeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = InterestIncome
        fields = '__all__'


class DividendIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DividendIncomeDocument
        fields = '__all__'


class DividendIncomeSerializer(serializers.ModelSerializer):
    documents = DividendIncomeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DividendIncome
        fields = '__all__'


class GiftIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftIncomeDocument
        fields = '__all__'


class GiftIncomeDetailsSerializer(serializers.ModelSerializer):
    gift_income_details = GiftIncomeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = GiftIncomeDetails
        fields = '__all__'


class FamilyPensionIncomeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyPensionIncomeInfo
        fields = '__all__'


class FamilyPensionIncomeSerializer(serializers.ModelSerializer):
    family_pension_income_docs = FamilyPensionIncomeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = FamilyPensionIncome
        fields = '__all__'


class ForeignIncomeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForeignIncomeInfo
        fields = '__all__'


class ForeignIncomeSerializer(serializers.ModelSerializer):
    foreign_income_docs = ForeignIncomeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = ForeignIncome
        fields = '__all__'


class WinningIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WinningIncomeDocument
        fields = '__all__'


class WinningIncomeSerializer(serializers.ModelSerializer):
    winnings_income_docs = WinningIncomeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = WinningIncome
        fields = '__all__'


class AgricultureIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgricultureIncomeDocument
        fields = '__all__'


class AgricultureIncomeSerializer(serializers.ModelSerializer):
    agriculture_income_docs = AgricultureIncomeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = AgricultureIncome
        fields = '__all__'


class Section80GSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section80G
        fields = '__all__'


class Section80ETTATTBUSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section80ETTATTBU
        fields = '__all__'


class Section80CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section80C
        fields = '__all__'


class Section80DFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section80DFile
        fields = '__all__'


class Section80DSerializer(serializers.ModelSerializer):
    section_80d_documents = Section80DFileSerializer(many=True, read_only=True)

    class Meta:
        model = Section80D
        fields = '__all__'


class DeductionsSerializer(serializers.ModelSerializer):
    section_80g = Section80GSerializer(many=True, read_only=True)
    section_80ettattbu = Section80ETTATTBUSerializer(read_only=True)
    section_80c = Section80CSerializer(many=True, read_only=True)
    section_80d = Section80DSerializer(read_only=True)

    class Meta:
        model = Deductions
        fields = '__all__'


class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFilingCertificate
        fields = '__all__'


class ServiceRequestTasksSerializer(serializers.Serializer):
    personal_information = PersonalInformationSerializer(read_only=True)
    tax_paid_details = TaxPaidDetailsSerializer(read_only=True)
    salary_income_details = SalaryIncomeSerializer(read_only=True)
    other_income_details = OtherIncomeDetailsSerializer(many=True, read_only=True)
    foreign_income_details = NRIEmployeeSalaryDetailsSerializer(read_only=True)
    house_property_details = HousePropertyIncomeDetailsSerializer(many=True, read_only=True)
    other_income = InterestIncomeSerializer(many=True, read_only=True)
    dividend_income = DividendIncomeSerializer(many=True, read_only=True)
    gift_income = GiftIncomeDetailsSerializer(many=True, read_only=True)
    family_pension_income = FamilyPensionIncomeSerializer(many=True, read_only=True)
    foreign_income = ForeignIncomeSerializer(many=True, read_only=True)
    winnings = WinningIncomeSerializer(many=True, read_only=True)
    agriculture_income = AgricultureIncomeSerializer(many=True, read_only=True)
    deductions = DeductionsSerializer(many=True, read_only=True)
    ITR_review_filing_certificate = ReviewFilingCertificateSerializer(read_only=True)


class ServiceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTask
        fields = [
            'id',
            'service_type',
            'category_name',
            'status',
            'created_at',
            'updated_at',
            'due_date',
            'priority',
            'completion_percentage',
            'service_request',
            'client',
            'assignee',
            'reviewer'
        ]


class ServiceTaskWithDataSerializer(serializers.ModelSerializer):
    task_data = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTask
        fields = [
            'id',
            'service_type',
            'category_name',
            'status',
            'created_at',
            'updated_at',
            'due_date',
            'priority',
            'completion_percentage',
            'service_request',
            'client',
            'assignee',
            'reviewer',
            'task_data'
        ]

    def get_task_data(self, obj):
        service_request = obj.service_request

        # Map category names to their corresponding models and serializers
        category_mapping = {
            'Personal Information': (PersonalInformation, PersonalInformationSerializer),
            'Tax Paid Details': (TaxPaidDetails, TaxPaidDetailsSerializer),
            'Salary Income': (SalaryIncome, SalaryIncomeSerializer),
            'Other Income Details': (OtherIncomeDetails, OtherIncomeDetailsSerializer),
            'Foreign Income Details': (NRIEmployeeSalaryDetails, NRIEmployeeSalaryDetailsSerializer),
            'House Property Details': (HousePropertyIncomeDetails, HousePropertyIncomeDetailsSerializer),
            'Interest Income': (InterestIncome, InterestIncomeSerializer),
            'Dividend Income': (DividendIncome, DividendIncomeSerializer),
            'Gift Income': (GiftIncomeDetails, GiftIncomeDetailsSerializer),
            'Family Pension Income': (FamilyPensionIncome, FamilyPensionIncomeSerializer),
            'Foreign Income': (ForeignIncome, ForeignIncomeSerializer),
            'Winning Income': (WinningIncome, WinningIncomeSerializer),
            'Agriculture Income': (AgricultureIncome, AgricultureIncomeSerializer),
            'Deductions': (Deductions, DeductionsSerializer),
            'Review Filing Certificate': (ReviewFilingCertificate, ReviewFilingCertificateSerializer)
        }

        if obj.category_name in category_mapping:
            model_class, serializer_class = category_mapping[obj.category_name]

            # For models that can have multiple records
            if obj.category_name in ['Other Income Details', 'House Property Details', 'Interest Income',
                                     'Dividend Income', 'Gift Income', 'Family Pension Income',
                                     'Foreign Income', 'Winning Income', 'Agriculture Income', 'Deductions']:
                data = model_class.objects.filter(service_request=service_request)
                if data.exists():
                    return serializer_class(data, many=True).data
            else:
                # For models that have one-to-one relationship
                data = model_class.objects.filter(service_request=service_request).first()
                if data:
                    return serializer_class(data).data

        return None


class CapitalGainsPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalGainsProperty
        fields = '__all__'


class CapitalGainsApplicableDetailsSerializer(serializers.ModelSerializer):
    gains_applicable = serializers.JSONField(required=False, allow_null=True)
    capital_gains_property_details = CapitalGainsPropertySerializer(many=True, read_only=True)

    class Meta:
        model = CapitalGainsApplicableDetails
        fields = '__all__'


class CapitalGainsEquityMutualFundDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalGainsEquityMutualFundDocument
        fields = '__all__'


class CapitalGainsEquityMutualFundSerializer(serializers.ModelSerializer):
    equity_mutual_fund_type = serializers.JSONField(required=False, allow_null=True)
    documents = CapitalGainsEquityMutualFundDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = CapitalGainsEquityMutualFund
        fields = '__all__'


class OtherCapitalGainsDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherCapitalGainsDocument
        fields = '__all__'


class OtherCapitalGainsSerializer(serializers.ModelSerializer):
    # Using the custom serializer for documents to handle multiple file uploads
    documents = OtherCapitalGainsDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = OtherCapitalGains
        fields = '__all__'


class BusinessProfessionalIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfessionalIncomeDocument
        fields = '__all__'


class BusinessProfessionalIncomeSerializer(serializers.ModelSerializer):
    opting_data = serializers.JSONField(required=False, allow_null=True)
    documents = serializers.SerializerMethodField()

    class Meta:
        model = BusinessProfessionalIncome
        fields = '__all__'

    def get_documents(self, obj):
        doc_types = ['26AS', 'AIS', 'GST Returns', 'Bank Statements', 'Other']
        grouped = {}
        for doc_type in doc_types:
            files = obj.documents.filter(document_type=doc_type)
            grouped[doc_type] = {
                "count": files.count(),
                "files": [
                    {
                        "id": f.id,
                        "url": f.file.url if f.file else None,
                        "uploaded_at": f.uploaded_at
                    }
                    for f in files
                ]
            }
        return grouped


class BusinessProfessionalIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfessionalIncomeDocument
        fields = ['id', 'document_type', 'file', 'uploaded_at']