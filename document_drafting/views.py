import json
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from .helpers import process_and_generate_draft_pdf
from django.db import transaction
from django.db.models import Count
from collections import defaultdict


@api_view(['GET', 'POST'])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def events_list_create(request):
    if request.method == 'GET':
        events = Events.objects.all()
        serializer = EventsSerializer(events, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EventsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def events_detail(request, pk):
    try:
        event = Events.objects.get(pk=pk)
    except Events.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EventsSerializer(event)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EventsSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def document_list_create(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            serializer = DocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def document_detail(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if 'template' in request.data and document.template:
            # Delete the old template file if it exists
            document.template.storage.delete(document.template.name)
            print(document.template.name)
        serializer = DocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        document.template.storage.delete(document.template.name)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def document_fields_list_create(request):
    if request.method == 'GET':
        fields = DocumentFields.objects.all()
        serializer = DocumentFieldsSerializer(fields, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DocumentFieldsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def document_fields_detail(request, pk):
    try:
        field = DocumentFields.objects.get(pk=pk)
    except DocumentFields.DoesNotExist:
        return Response({'error': 'Document field not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentFieldsSerializer(field)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DocumentFieldsSerializer(field, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        field.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def document_fields_by_document(request, document_id):
    try:
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        fields = document.fields.all()
        document = DocumentSerializer(document)
        print(document.data['template'])
        serializer = DocumentFieldsSerializer(fields, many=True)
        return Response({'fields':serializer.data, 'template': document.data['template']}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def document_template_and_fields(request, id):
    try:
        context = ContextWiseEventAndDocument.objects.get(pk=id)
    except ContextWiseEventAndDocument.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    print(request.user)

    fields = context.document.fields.all()
    document = DocumentSerializer(context.document)
    serializer = DocumentFieldsSerializer(fields, many=True)
    draft_info = DocumentDraftDetailSerializer(DocumentDraftDetail.objects.filter(draft=context), many=True).data
    return Response({
        'template': document.data['template'],
        'fields': serializer.data,
        'draft_info': draft_info
    })


@api_view(['GET', 'POST'])
def user_document_draft_list_create(request):
    if request.method == 'GET':
        drafts = UserDocumentDraft.objects.all()
        serializer = UserDocumentDraftSerializer(drafts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        try:
            context = UserDocumentDraft.objects.get(context=request.data.get('context'))
        except:
            serializer = UserDocumentDraftSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User document draft already exists for this context'})


@api_view(['GET', 'PUT', 'DELETE'])
def user_document_draft_detail(request, pk):
    try:
        draft = UserDocumentDraft.objects.get(pk=pk)
    except UserDocumentDraft.DoesNotExist:
        return Response({'error': 'User document draft not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserDocumentDraftSerializer(draft)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserDocumentDraftSerializer(draft, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        draft.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def context_wise_event_and_document(request, event_instance):
    """
    Returns event instance details, base event info, and all related documents.
    """
    try:
        # 1. Get event instance
        instance = EventInstance.objects.select_related('event').get(pk=event_instance)

        # 2. Get all related documents
        documents = ContextWiseEventAndDocument.objects.filter(event_instance=instance)

        if not documents.exists():
            return Response({'error': 'No documents found for this event instance'}, status=status.HTTP_404_NOT_FOUND)

        # 3. Serialize results
        event_instance_data = EventInstanceSerializer(instance).data
        document_data = ContextWiseEventAndDocumentEventSerializer(documents, many=True).data

        # 4. Structure response
        response = {
            'event_instance': event_instance_data,
            'documents': document_data
        }

        return Response(response, status=status.HTTP_200_OK)

    except EventInstance.DoesNotExist:
        return Response({'error': 'Event instance not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def draft_document_details_create(request):
    if request.method == 'GET':
        drafts = DocumentDraftDetail.objects.all()
        serializer = DocumentDraftDetailSerializer(drafts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
        draft_data = data.get('draft_data')

        if isinstance(draft_data, str):
            try:
                data['draft_data'] = json.dumps(json.loads(draft_data))
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON for draft_data'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentDraftDetailSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            if data.get('status') == 'completed':
                # Process the draft and generate PDF if status is completed
                if instance.file:
                    instance.file.storage.delete(instance.file.name)
                process_and_generate_draft_pdf(instance)
            return Response(DocumentDraftDetailSerializer(instance).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def draft_document_details(request, pk):
    try:
        draft = DocumentDraftDetail.objects.get(pk=pk)
    except DocumentDraftDetail.DoesNotExist:
        return Response({'error': 'Draft document detail not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentDraftDetailSerializer(draft)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data.copy()
        draft_data = data.get('draft_data')

        if isinstance(draft_data, str):
            try:
                data['draft_data'] = json.dumps(json.loads(draft_data))
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON for draft_data'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DocumentDraftDetailSerializer(draft, data=data)
        if serializer.is_valid():
            instance = serializer.save()

            if data.get('status') == 'completed':
                # Process the draft and generate PDF if status is completed
                if instance.file:
                    instance.file.storage.delete(instance.file.name)
                process_and_generate_draft_pdf(instance)
            return Response(DocumentDraftDetailSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        draft.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def draft_document_by_event(request):
    if request.method == 'POST':
        event_id = request.data.get('event')
        if not event_id:
            return Response({'error': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():

            # Create the event instance
            try:
                event = get_object_or_404(Events, pk=event_id)
                event_instance = EventInstance.objects.create(
                    event=event
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            data = request.data.copy()
            data['event_instance'] = event_instance.id
            documents = data.pop('documents', [])

            if not documents:
                return Response({'error': 'At least one document is required'}, status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(documents, list):
                documents = [documents]

            created = []
            errors = []

            for doc_id in documents:
                try:
                    document = Document.objects.get(pk=doc_id)
                    record_data = data.copy()
                    record_data['document'] = document.id
                    serializer = ContextWiseEventAndDocumentSerializer(data=record_data)
                    if serializer.is_valid():
                        serializer.save()
                        created.append(serializer.data)
                    else:
                        errors.append({f'document_id_{doc_id}': serializer.errors})
                except Document.DoesNotExist:
                    errors.append({f'document_id_{doc_id}': 'Document does not exist'})

            response_payload = {
                'event_instance_id': event_instance.id,
                'created': created
            }

            if errors:
                response_payload['errors'] = errors
                return Response(response_payload, status=status.HTTP_207_MULTI_STATUS)

            return Response(response_payload, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def user_document_draft_is_exist(request, context_id):
    """
    Check if a user document draft exists for the given context.
    """
    try:
        draft = UserDocumentDraft.objects.get(context=context_id)
        serializer = UserDocumentDraftSerializer(draft)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserDocumentDraft.DoesNotExist:
        return Response({'error': 'User document draft not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def document_status_list(request, context_id):
    try:
        queryset = ContextWiseEventAndDocument.objects.filter(context=context_id).order_by('-id')

        serializer = ContextWiseEventAndDocumentStatusSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def context_wise_event_and_document_list_create(request):
    if request.method == 'GET':
        queryset = ContextWiseEventAndDocument.objects.select_related(
            'category',
            'event_instance__event',
            'created_by'
        ).all()
        serializer = ContextWiseEventAndDocumentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        try:
            serializer = ContextWiseEventAndDocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def context_wise_event_and_document_detail(request, pk):
    try:
        instance = ContextWiseEventAndDocument.objects.get(pk=pk)
    except ContextWiseEventAndDocument.DoesNotExist:
        return Response({'error': 'ContextWiseEventAndDocument not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ContextWiseEventAndDocumentSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = ContextWiseEventAndDocumentSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def category_filter_events(request, category_id):
    """
    Returns a list of events filtered by category.
    """
    if request.method == 'GET':
        try:
            category = Category.objects.get(pk=category_id)
            events = category.events.all()
            serializer = EventsSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def category_or_event_wise_document_list(request):
    """
    Returns a list of documents associated with a specific event instance.
    """
    if request.method == 'GET':
        try:
            event_id = request.query_params.get('event_id', None)
            category_id = request.query_params.get('category_id', None)
            filter_fields ={}
            if event_id:
                filter_fields['event'] = event_id
            if category_id:
                filter_fields['category'] = category_id
            documents = Document.objects.filter(**filter_fields)
            serializer = DocumentSerializer(documents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EventInstance.DoesNotExist:
            return Response({'error': 'Event instance not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def my_events_list(request):
    """
    Returns a list of event instances associated with the user's context.
    """
    context_id = request.query_params.get('doc_drafts_id', None)
    if not context_id:
        return Response({'error': 'Context is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch all documents linked to this context
        drafts = ContextWiseEventAndDocument.objects.filter(context_id=context_id)
        if not drafts.exists():
            return Response([])

        # Extract unique event_instance IDs
        event_instance_ids = drafts.values_list('event_instance_id', flat=True).distinct()

        # Fetch corresponding event instances
        event_instances = EventInstance.objects.filter(id__in=event_instance_ids).order_by('-id')

        serializer = EventInstanceSerializer(event_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def document_summary_by_context(request):
    """
    Returns summarized document status counts for a given context.
    Summary includes: Total Document, Draft, Finalized, Action Pending.
    """
    context_id = request.query_params.get('doc_draft_id')

    if not context_id:
        return Response({'error': 'Context ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Group and count documents by status
        status_counts = ContextWiseEventAndDocument.objects.filter(
            context_id=context_id
        ).values('status').annotate(count=Count('id'))

        count_map = defaultdict(int)
        for entry in status_counts:
            count_map[entry['status']] = entry['count']

        draft = count_map['draft']
        finalized = count_map['completed']
        action_pending = count_map['yet_to_start'] + count_map['in_progress']
        total = sum(count_map.values())

        return Response({
            "Total Document": total,
            "Draft": draft,
            "Finalized": finalized,
            "Action Pending": action_pending
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def filter_documents_by_status(request):
    """
    Returns documents filtered by status for a given context.
    """
    doc_status = request.query_params.get('status', None)  # renamed to avoid conflict
    context_id = request.query_params.get('doc_draft_id', None)

    if not doc_status or not context_id:
        return Response({'error': 'Status and context ID are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        documents = ContextWiseEventAndDocument.objects.filter(
            status=doc_status,
            context_id=context_id
        )
        serializer = ContextWiseEventAndDocumentStatusSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 1. GET all and POST new
@api_view(['GET', 'POST'])
def favourite_document_list_create(request):
    if request.method == 'GET':
        favourites = UserFavouriteDocument.objects.all()
        serializer = UserFavouriteDocumentSerializer(favourites, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        draft_id = request.data.get('draft')
        if draft_id:
            favourite_count = UserFavouriteDocument.objects.filter(draft_id=draft_id).count()
            if favourite_count >= 5:
                return Response(
                    {"error": "You can only favourite up to 5 documents per draft."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = UserFavouriteDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. GET, PUT, DELETE by pk
@api_view(['GET', 'PUT', 'DELETE'])
def favourite_document_detail(request, pk):
    try:
        favourite = UserFavouriteDocument.objects.get(pk=pk)
    except UserFavouriteDocument.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserFavouriteDocumentSerializer(favourite)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserFavouriteDocumentSerializer(favourite, data=request.data)
        if serializer.is_valid():
            draft_id = request.data.get('draft')
            if draft_id:
                current_count = UserFavouriteDocument.objects.filter(draft_id=draft_id).exclude(id=pk).count()
                if current_count >= 5:
                    return Response(
                        {"error": "You can only favourite up to 5 documents per draft."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 3. GET favourites by draft_id
@api_view(['GET'])
def favourite_documents_by_draft(request, draft_id):
    favourites = UserFavouriteDocument.objects.filter(draft_id=draft_id)
    serializer = UserFavouriteDocumentSerializer(favourites, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def recent_events_by_context(request, context_id):
    qs = (
        ContextWiseEventAndDocument.objects
        .filter(context_id=context_id, event_instance__isnull=False)
        .select_related('event_instance__event')
        .order_by('-updated_at')
    )

    seen_events = set()
    unique_events = []
    for item in qs:
        event = item.event_instance.event if item.event_instance else None
        if event and event.pk not in seen_events:
            unique_events.append(event)
            seen_events.add(event.pk)
        if len(unique_events) == 5:
            break

    serializer = EventsSerializer(unique_events, many=True)  # define this serializer
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def recent_documents_by_context(request, context_id):
    qs = (
        ContextWiseEventAndDocument.objects
        .filter(context_id=context_id, document__isnull=False)
        .select_related('document')
        .order_by('-updated_at')
    )

    seen_docs = set()
    unique_documents = []
    for item in qs:
        doc = item.document
        if doc and doc.pk not in seen_docs:
            unique_documents.append(doc)
            seen_docs.add(doc.pk)
        if len(unique_documents) == 5:
            break

    serializer = DocumentSerializer(unique_documents, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)