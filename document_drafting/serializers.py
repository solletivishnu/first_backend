from rest_framework import serializers
from .models import *
import json


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    events = EventsSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = "__all__"


class DocumentFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFields
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class UserDocumentDraftSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDocumentDraft
        fields = '__all__'


class UserFavouriteDocumentSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()

    class Meta:
        model = UserFavouriteDocument
        fields = '__all__'

    def get_document(self, obj):
        if obj.document:
            return {
                'id': obj.document.id,
                'document_name': obj.document.document_name,
                'description': obj.document.description,
                'template': obj.document.template,
            }
        return None


class EventInstanceSerializer(serializers.ModelSerializer):
    event_name = serializers.SerializerMethodField()

    class Meta:
        model = EventInstance
        fields = '__all__'

    def get_event_name(self, obj):
        if obj.event:
            return {
                'id': obj.event.id,
                'event_name': obj.event.event_name,
            }
        return None


class ContextWiseEventAndDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContextWiseEventAndDocument
        fields = '__all__'


class ContextWiseEventAndDocumentEventSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()

    class Meta:
        model = ContextWiseEventAndDocument
        fields = ["id", "document", "status", "updated_at"]

    def get_document(self, obj):
        if obj.document:
            return {
                "id": obj.document.id,
                "name": obj.document.document_name,
                "description": obj.document.description,
                "template": obj.document.template.url if obj.document.template else None,
            }
        return None



class DocumentDraftDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentDraftDetail
        fields = '__all__'


class ContextWiseEventAndDocumentStatusSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created_at', format="%d/%m/%y")
    last_edited = serializers.DateTimeField(source='updated_at', format="%d/%m/%y")
    category = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()

    class Meta:
        model = ContextWiseEventAndDocument
        fields = ['id', 'created_date', 'document','category', 'event', 'status', 'last_edited', 'creator', 'file']

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.category_name
            }
        return None

    def get_event(self, obj):
        if obj.event_instance and obj.event_instance.event:
            return {
                "id": obj.event_instance.event.id,
                "name": obj.event_instance.event.event_name,
                "event_instance_id": obj.event_instance.id
            }
        return None

    def get_document(self, obj):
        if obj.document:
            return {
                "id": obj.document.id,
                "name": obj.document.document_name,
                "description": obj.document.description,
            }
        return None

    def get_creator(self, obj):
        user = obj.created_by
        if not user:
            return ""

        first = user.first_name if user.first_name else ""
        middle = user.middle_name if hasattr(user, 'middle_name') and user.middle_name else ""
        last = user.last_name if user.last_name else ""

        full_name = " ".join(part for part in [first, middle, last] if part)
        return full_name or ""

    def get_status(self, obj):
        status_map = {
            'completed': 'Completed',
            'in_progress': 'Processed',
            'draft': 'Declined',
            'yet_to_start': 'Yet to Start',
        }
        return status_map.get(obj.status, obj.status.title())

    def get_file(self, obj):
        if hasattr(obj, 'draft_details') and obj.draft_details.file:
            request = self.context.get('request')
            file_url = obj.draft_details.file.url
            # Build absolute URL if request context is present
            return request.build_absolute_uri(file_url) if request else file_url
        return None