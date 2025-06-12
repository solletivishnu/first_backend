import os
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from usermanagement.models import Context, ServiceRequest  # Update this import as per your project


def personal_information_pan(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'personal_information_pan', filename)


def personal_information_aadhar(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'personal_information_aadhar', filename)


def tax_paid_details_file(instance, filename):
    # instance is of TaxPaidDetailsFile
    service_request_id = str(instance.tax_paid.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'tax_paid_details_file', document_type, filename
    )


def salary_income_details_file(instance, filename):
    # instance is of TaxPaidDetailsFile
    service_request_id = str(instance.income.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'salary_income_details_file', document_type, filename
    )


def outcome_income_details_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.other_income_details.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'outcome_income_details_file', filename)


def foreign_emp_salary_details_file(instance, filename):
    # instance is of ForeignEmpSalaryDetailsFile
    service_request_id = str(instance.nri.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'foreign_emp_salary_details_file', document_type, filename
    )


def house_property_details_municipal_tax_receipt(instance, filename):
    # instance is of HousePropertyDetailsMunicipalTaxReceipt
    service_request_id = str(instance.house_property_details.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'house_property_details_municipal_tax_receipt', filename)


def house_property_details_loan_statement(instance, filename):
    # instance is of HousePropertyDetailsOwnershipDocument
    service_request_id = str(instance.house_property_details.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'house_property_details_loan_statement', filename)


def house_property_details_loan_interest_certificate(instance, filename):
    # instance is of HousePropertyDetailsOwnershipDocument
    service_request_id = str(instance.house_property_details.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'house_property_details_loan_interest_certificate', filename)


def interest_income_details_file(instance, filename):
    # instance is of InterestIncomeDetailsFile
    service_request_id = str(instance.interest_income.service_request.id)
    interest_type = instance.interest_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'interest_income_details_file', interest_type, filename
    )


def dividend_income_file(instance, filename):
    # instance is of DividendIncomeFile
    service_request_id = str(instance.dividend_income.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'dividend_income_file', filename
    )


def winning_income_file(instance, filename):
    # instance is of DividendIncomeFile
    service_request_id = str(instance.winning_income.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'winning_income_file', filename
    )


def agriculture_income_file(instance, filename):
    # instance is of DividendIncomeFile
    service_request_id = str(instance.agriculture_income.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'agriculture_income_file', filename
    )


def review_filing_certificate(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'review_filing_certificate', filename)


def draft_filing_certificate(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'draft_filing_certificate', filename)


def section_80g_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80g_file', filename)


def section_80ettattbu_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80ettattbu_file', filename)


def section_80e_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.section_80e.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80e_file', filename)


def section_80ee_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.section_80ee.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80ee_file', filename)


def section_80d_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.section_80d.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80d_file', filename)


def section_80ddb_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.section_80ddb.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80ddb_file', filename)


def section_80eeb_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.section_80eeb.deductions.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80eeb_file', filename)


def capital_gains_property_purchase_doc(instance, filename):
    # instance is of CapitalGainsPropertyPurchaseDoc
    service_request_id = str(instance.capital_gains_applicable.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'capital_gains_property_purchase_doc', filename
    )


def capital_gains_property_sale_doc(instance, filename):
    # instance is of CapitalGainsPropertySaleDoc
    service_request_id = str(instance.capital_gains_applicable.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'capital_gains_property_sale_doc', filename
    )


def capital_gains_property_reinvestment_docs(instance, filename):
    # instance is of CapitalGainsStocksPurchaseDoc
    service_request_id = str(instance.capital_gains_applicable.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'capital_gains_stocks_purchase_doc', filename
    )


def capital_gains_equity_mutual_fund_file(instance, filename):
    # instance is of CapitalGainsEquityMutualFundFile
    service_request_id = str(instance.capital_gains_equity_mutual_fund.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'capital_gains_equity_mutual_fund_file', filename
    )


def other_capital_gains_file(instance, filename):
    # instance is of OtherIncomeFile
    service_request_id = str(instance.other_capital_gains_info.other_capital_gains.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'other_income_file', filename
    )


def business_professional_income_file(instance, filename):
    # instance is of BusinessProfessionalIncomeFile
    service_request_id = str(instance.business_professional_income_info.business_professional_income.service_request_id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'business_professional_income_file',document_type,  filename
    )


def foreign_income_file(instance, filename):
    # instance is of ForeignIncomeFile
    service_request_id = str(instance.foreign_income.service_request_id)


    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'foreign_income_file', "form 67", filename
    )


def section_80c_file(instance, filename):
    # instance is of Section80CFile
    service_request_id = str(instance.section_80c.deductions.service_request_id)

    # Construct an upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'section_80c_file', filename)
