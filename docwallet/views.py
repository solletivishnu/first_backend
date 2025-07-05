from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import DocWallet, Folder, Document
from .serializers import DocWalletSerializer, FolderSerializer, DocumentSerializer, DocWalletDocSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import boto3
from Tara.settings.default import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_PRIVATE_BUCKET_NAME
from django.http import JsonResponse
from urllib.parse import urlparse, unquote
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import re
from .helpers import *
# CRUD operations for DocWallet


@api_view(['GET', 'POST'])
def docwallet_list_create(request):
    if request.method == 'GET':
        docwallets = DocWallet.objects.all()
        serializer = DocWalletSerializer(docwallets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DocWalletSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def docwallet_detail(request, pk):
    try:
        docwallet = DocWallet.objects.get(pk=pk)
    except DocWallet.DoesNotExist:
        return Response({'error': 'DocWallet not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocWalletSerializer(docwallet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DocWalletSerializer(docwallet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        docwallet.delete()
        return Response({'message': 'DocWallet deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# CRUD operations for Folder
@api_view(['GET', 'POST'])
def folder_list_create(request):
    if request.method == 'GET':
        folders = Folder.objects.all()
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            new_folder = serializer.save()

            parent = new_folder.parent
            # Check if the parent folder is "CurrentWorkPapers"
            if parent and parent.name == 'CurrentWorkingPapers':
                fy_folder_name = new_folder.name.strip()

                # Regex: matches patterns like '2023-24', '2020-21'
                # NOTE FOR FUTURE DEVELOPERS:
                # This logic assumes financial years are in the format 20XX-YY and only valid till 2098-2099.
                # If you're working in or beyond the year 2099, follow the below Line
                # update this regex and logic to support formats like '2099-00', '2100-01', etc.
                if re.fullmatch(r'20\d{2}-\d{2}', fy_folder_name):
                    subfolder_names = [
                        'Financial Statements',
                        'Bank Statements',
                        'Income Tax Filings',
                        'Payroll'
                    ]
                    for name in subfolder_names:
                        Folder.objects.create(
                            name=name,
                            wallet=new_folder.wallet,
                            parent=new_folder
                        )

            return Response(FolderSerializer(new_folder).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def folder_detail(request, pk):
    try:
        folder = Folder.objects.get(pk=pk)
    except Folder.DoesNotExist:
        return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FolderSerializer(folder)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FolderSerializer(folder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        folder.delete()
        return Response({'message': 'Folder deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# CRUD operations for Document
@api_view(['POST'])
def document_list_create(request):
    # Use MultiPartParser to handle file uploads
    parser_classes = [MultiPartParser, FormParser]

    # Check if files are provided
    if 'files' not in request.FILES:
        return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve the folder ID from the request data
    folder_id = request.data.get('folder', None)
    if not folder_id:
        return Response({"error": "Folder ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        folder = Folder.objects.get(pk=folder_id)
    except Folder.DoesNotExist:
        return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)

    # Process each file
    files = request.FILES.getlist('files')
    documents = []

    for file in files:
        document = Document(file=file, folder=folder)
        document.save()  # Save the document (filename will be auto-assigned)
        documents.append(document)

    # Serialize the documents and return the response
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def document_detail(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = DocumentSerializer(document, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        document.delete()
        return Response({'message': 'Document deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def list_folders_and_files(request, folder_id):
    try:
        # Retrieve the parent folder by ID
        parent_folder = Folder.objects.get(pk=folder_id)
    except Folder.DoesNotExist:
        return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

    # Fetch all subfolders of the current folder
    subfolders = Folder.objects.filter(parent=parent_folder)

    # Fetch all documents in the current folder
    documents = Document.objects.filter(folder=parent_folder)

    # Serialize the data for folders and documents
    folder_serializer = FolderSerializer(subfolders, many=True)
    document_serializer = DocumentSerializer(documents, many=True)

    # Return the response with folders and files
    return Response({
        'folder': FolderSerializer(parent_folder).data,
        'subfolders': folder_serializer.data,
        'documents': document_serializer.data
    })


def documents_view(request):
    # Get the URL from the query parameters
    document_url = request.GET.get('url', None)

    if not document_url:
        return JsonResponse({'error': 'URL parameter is required'}, status=400)

    try:
        # Parse the URL to extract the file name (Key)
        parsed_url = urlparse(document_url)
        file_key = unquote(parsed_url.path.lstrip('/'))  # Remove leading '/' and decode URL

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        # Generate a pre-signed URL
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': AWS_PRIVATE_BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )

        # Return the pre-signed URL
        return JsonResponse({'url': file_url}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def list_last_10_uploaded_files(request):
    """
    API endpoint to list the last 10 uploaded files for a given context_id.
    The context_id will be linked via the Folder's context.
    """
    context_id = request.query_params.get('context_id', None)

    if not context_id:
        return Response({"error": "context_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the last 10 documents for the given context_id through Folder's context
        documents = Document.objects.filter(
            folder__wallet__context__id=context_id
        ).order_by('-uploaded_at')[:10]  # Last 10 files based on upload date

        # Prepare the response data
        documents_data = [
            {
                "name": document.name,
                "file_url": document.file.url,  # Assuming file URL is stored correctly in the file field
                "uploaded_at": document.uploaded_at
            }
            for document in documents
        ]

        return Response({"documents": documents_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def delete_all_files_in_folder(folder):
    """
    Recursively delete all files in a folder and its subfolders.
    This will ensure that files are deleted from both the database and S3.
    """
    # Delete all documents (files) in the current folder
    for document in folder.documents.all():
        # Remove the file from S3
        document.file.storage.delete(document.file.name)  # Deletes the file from S3
        document.delete()  # Delete the document (file) from the database

    # Recursively delete all files in subfolders
    subfolders = folder.subfolders.all()  # Get all subfolders of the current folder
    for subfolder in subfolders:
        delete_all_files_in_folder(subfolder)  # Recursively delete files in subfolder
        subfolder.delete()  # After deleting files, delete the subfolder itself


root_folder_names = ['PermanentWorkingPapers', 'CurrentWorkPapers', 'OtherDocuments']

@api_view(['DELETE'])
def delete_folder(request, folder_id):
    """
    Deletes the folder and all its files (including files in subfolders).
    Prevents deletion of root folders like 'PermanentWorkingPapers', etc.
    """
    try:
        # Retrieve the folder to be deleted
        folder = get_object_or_404(Folder, id=folder_id)

        # Check if the folder name is one of the protected root folder names
        if folder.name in root_folder_names:
            return Response({"error": "You cannot delete the root folder"}, status=400)

        # Delete all files in the folder and its subfolders
        delete_all_files_in_folder(folder)

        # Finally, delete the folder itself
        folder.delete()

        return Response({"message": "Folder and its files have been deleted successfully"}, status=200)

    except Folder.DoesNotExist:
        return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def remove_document(request, file_id):
    """
    Removes a specific document (file) from the folder and storage (S3).
    """
    try:
        # Get the document (file) to be removed
        document = get_object_or_404(Document, id=file_id)

        # Delete the file from S3 (if using django-storages)
        document.file.storage.delete(document.file.name)  # This will delete the file from S3

        # Delete the document (file) from the database
        document.delete()

        return Response({"message": "File has been removed successfully"}, status=200)

    except Document.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def retrieve_docwallet_info(request):
    """
    Retrieves the Document Wallet information based on the context_id.
    The user provides the context_id, and the API returns only the parent folder structure (no subfolders).
    """
    context_id = request.query_params.get('context_id')

    # Check if context_id is provided
    if not context_id:
        return Response({"error": "context_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the DocWallet object for the given context_id
        docwallet = get_object_or_404(DocWallet, context_id=context_id)
    except DocWallet.DoesNotExist:
        return Response({"error": "DocWallet not found for the given context_id."}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve the parent folders (root folders only) for the given DocWallet
    root_folders = Folder.objects.filter(wallet=docwallet, parent=None)

    # Serialize the root folders (parent folders) only
    serializer = FolderSerializer(root_folders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def retrieve_recent_files(request):
    """
    Retrieves the 10 most recent files uploaded based on the context_id.
    """
    context_id = request.query_params.get('context_id')

    if not context_id:
        return Response({"error": "context_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the context_id exists in the DocWallet model
    try:
        docwallet = DocWallet.objects.get(context_id=context_id)
    except DocWallet.DoesNotExist:
        return Response({"error": "DocWallet not found for the given context_id."}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve the 10 most recent documents uploaded for the given context_id
    recent_files = Document.objects.filter(
        folder__wallet=docwallet
    ).order_by('-accessed_at')[:10]

    if not recent_files:
        return Response({"message": "No files found for the given context_id."}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the document data
    serializer = DocumentSerializer(recent_files, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


def fetch_document_data(request):
    # Get the URL from the query parameters
    document_url = request.GET.get('url', None)

    if not document_url:
        return JsonResponse({'error': 'URL parameter is required'}, status=400)

    try:
        # Parse the URL to extract the file name (Key)
        parsed_url = urlparse(document_url)
        file_key = unquote(parsed_url.path.lstrip('/'))  # Remove leading '/' and decode URL

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        # Fetch the file from S3
        s3_object = s3_client.get_object(Bucket=AWS_PRIVATE_BUCKET_NAME, Key=file_key)

        # Get the content of the file
        file_data = s3_object['Body'].read()

        # Get the content type (MIME type) of the file
        content_type = s3_object.get('ContentType', 'application/octet-stream')

        # Return the content as an HTTP response with appropriate content type
        response = HttpResponse(file_data, content_type=content_type)

        # Optionally, set a filename in the Content-Disposition header to suggest a filename
        response['Content-Disposition'] = f'inline; filename="{file_key}"'

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def context_file_autocomplete(request):
    query = request.GET.get("q", "").strip()
    print("Testing the Use case")
    context_id = request.user.active_context_id  # or however you access current context

    if not query:
        return Response({"results": []})

    if not context_id or context_id not in context_tries:
        return Response({"results": [], "message": "No trie found for context"}, status=404)

    suggestions = context_tries[context_id].search_prefix(query, limit=10)
    return Response({"results": suggestions})

@api_view(['GET'])
def context_file_filter(request):
    q = request.GET.get("q", "")
    context_id = request.user.active_context_id

    results = Document.objects.filter(
        folder__wallet__context_id=context_id,
        name__icontains=q
    ).select_related('folder', 'folder__wallet')[:20]

    serializer = DocumentSerializer(results, many=True)
    return Response({"results": serializer.data})