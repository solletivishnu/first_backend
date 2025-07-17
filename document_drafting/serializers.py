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
    is_favourite = serializers.SerializerMethodField()
    favourite_data = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'

    def get_is_favourite(self, obj):
        if hasattr(obj, 'user_favorites') and obj.user_favorites:
            return True
        draft_id = self.context.get('draft_id')
        if draft_id:
            return UserFavouriteDocument.objects.filter(
                document=obj,
                draft_id=draft_id
            ).exists()
        return False

    def get_favourite_data(self, obj):
        if hasattr(obj, 'user_favorites') and obj.user_favorites:
            return UserFavouriteDocumentSerializer(obj.user_favorites[0]).data
        draft_id = self.context.get('draft_id')
        if draft_id:
            favourite = UserFavouriteDocument.objects.filter(
                document=obj,
                draft_id=draft_id
            ).first()
            if favourite:
                return UserFavouriteDocumentSerializer(favourite).data.id
        return None


class UserDocumentDraftSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDocumentDraft
        fields = '__all__'


class UserFavouriteDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFavouriteDocument
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['document'] = {
            'id': instance.document.id,
            'name': instance.document.document_name,
            'description': instance.document.description,
            'template': instance.document.template.url if instance.document.template else None,
        }
        return representation


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
    file = serializers.SerializerMethodField()

    class Meta:
        model = ContextWiseEventAndDocument
        fields = ["id", "document", "status", "updated_at", "file_name", "file"]

    def get_document(self, obj):
        if obj.document:
            return {
                "id": obj.document.id,
                "name": obj.document.document_name,
                "description": obj.document.description,
                "template": obj.document.template.url if obj.document.template else None,
            }
        return None

    def get_file(self, obj):
        if hasattr(obj, 'draft_details') and obj.draft_details.file:
            request = self.context.get('request')
            file_url = obj.draft_details.file.url
            # Build absolute URL if request context is present
            return request.build_absolute_uri(file_url) if request else file_url
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
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = ContextWiseEventAndDocument
        fields = ['id', 'created_date', 'document','category', 'event', 'status', 'last_edited', 'creator', 'file', 'file_name']

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.category_name
            }
        if obj.event_instance and obj.event_instance.event and obj.event_instance.event.category:
            return {
                "id": obj.event_instance.event.category.id,
                "name": obj.event_instance.event.category.category_name
            }
        if obj.document and obj.document.category:
            return {
                "id": obj.document.category.id,
                "name": obj.document.category.category_name
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
            'draft': 'Draft',
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

    def get_file_name(self, obj):
        if obj.file_name:
            return obj.file_name
        if obj.document:
            return obj.document.document_name
        return None


class FilterDropdownDataSerializer(serializers.Serializer):
    document_names = serializers.ListField(child=serializers.CharField())
    event_names = serializers.ListField(child=serializers.CharField())
    category_names = serializers.ListField(child=serializers.CharField())
    statuses = serializers.ListField(child=serializers.CharField())
    created_by = serializers.ListField(child=serializers.CharField())