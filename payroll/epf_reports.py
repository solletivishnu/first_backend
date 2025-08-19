# views.py
from django.http import HttpResponse, FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import tempfile
import os
import pandas as pd
from openpyxl import Workbook
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from io import BytesIO


@api_view(['GET'])
@permission_classes([AllowAny])
def download_epf_template(request):
    """Generate an Excel file in memory and send it as a download."""

    # 1. Create a new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "ECRSheet_1"

    # 2. Define headers (same as your original columns)
    headers = [
        "UAN", "MEMBER NAME", "GROSS WAGES", "EPF WAGES", "EPS WAGES",
        "EDLI WAGES", "EPF CONTRI REMITTED", "EPS CONTRI REMITTED",
        "EPF EPS DIFF REMITTED", "NCP DAYS", "REFUND OF ADVANCES"
    ]

    # 3. Write headers to the first row
    for col_num, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_num, value=header)

    # 4. Save Excel file to memory (BytesIO buffer)
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)  # Move cursor to start of buffer

    # 5. Create HTTP response with the Excel file
    response = HttpResponse(
        excel_buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=EPF_Template.xlsx"

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def convert_epf_to_text(request):
    if 'file' not in request.FILES:
        return HttpResponse("No file uploaded", status=400)

    try:
        df = pd.read_excel(request.FILES['file'])
        text_content = df.apply(
            lambda row: "#~#".join(row.astype(str)),
            axis=1
        ).str.cat(sep="\r\n")

        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="EPF_Data.txt"'
        return response

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)