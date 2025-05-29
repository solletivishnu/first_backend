from rest_framework import serializers
from .models import DocWallet, Folder, Document
from usermanagement.models import Context


class DocWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocWallet
        fields = ['id', 'context', 'created_at']


class FolderSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all(), required=False)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'wallet', 'parent', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'file', 'folder', 'uploaded_at']


class FolderDataSerializer(serializers.ModelSerializer):
    subfolders = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ['name', 'created_at', 'subfolders']

    def get_subfolders(self, obj):
        # Recursively serialize subfolders
        subfolders = Folder.objects.filter(parent=obj)
        return FolderSerializer(subfolders, many=True).data


class DocWalletDocSerializer(serializers.ModelSerializer):
    folders = FolderSerializer(many=True)

    class Meta:
        model = DocWallet
        fields = ['context', 'created_at', 'folders']