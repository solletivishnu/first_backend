import os
import json
import requests
import pdfkit
from io import BytesIO
from jinja2 import Template
from django.core.files.base import ContentFile

def draft_document_file(instance, filename):
    """
    Generate a file path for the document draft based on the document name and user ID.
    """
    # Ensure the document name is safe for use in a file path
    document_name = instance.draft.document.document_name.replace(" ", "_").replace("/", "_")

    # Construct the file path
    return os.path.join('draft_files', document_name, str(instance.id), filename)


def document_template_path(instance, filename):
    """
    Generate a file path for the saved document based on the document name and user ID.
    """
    # Ensure the document name is safe for use in a file path
    document_name = instance.document_name.replace(" ", "_").replace("/", "_")

    # Construct the file path
    return os.path.join('document_drafting', 'document_templates', document_name, filename)


def process_and_generate_draft_pdf(instance):
    """
    Fetch HTML template, render it using draft_data, convert to PDF, and save to instance.file.
    """
    # 1. Get template URL from related document
    document = instance.draft.document
    if not document or not document.template:
        return

    try:
        # 2. Fetch the template file from S3 (or local if using default storage)
        template_url = document.template.url
        response = requests.get(template_url)
        if response.status_code != 200:
            raise Exception("Unable to fetch template")
        html_template = response.text
    except Exception as e:
        print(f"[Error] Template fetch failed: {e}")
        return

    options = {
        'encoding': "UTF-8",
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'margin-right': '10mm',
        'enable-local-file-access': '',  # if using local CSS/fonts
    }

    try:
        # 3. Render HTML using Jinja2 with draft_data context
        context = instance.draft_data or {}
        template = Template(html_template)
        rendered_html = template.render(**context)
    except Exception as e:
        print(f"[Error] HTML render failed: {e}")
        return

    try:
        # 4. Generate PDF from rendered HTML using wkhtmltopdf via pdfkit
        pdf_bytes = pdfkit.from_string(rendered_html, False, options=options)

        # 5. Save the PDF to the file field of the model
        filename = f"{document.document_name.replace(' ', '_')}.pdf"
        instance.file.save(filename, ContentFile(pdf_bytes))
    except Exception as e:
        print(f"[Error] PDF generation failed: {e}")
