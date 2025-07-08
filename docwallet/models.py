from django.db import models
from usermanagement.models import Context
import os
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from storages.backends.s3boto3 import S3Boto3Storage
from Tara.settings.default import AWS_PRIVATE_BUCKET_NAME
from .helpers import context_tries
from django.contrib.postgres.indexes import GinIndex
# Create your models here.


class PrivateS3Storage(S3Boto3Storage):
    bucket_name = AWS_PRIVATE_BUCKET_NAME
    custom_domain = f"{AWS_PRIVATE_BUCKET_NAME}.s3.amazonaws.com"  # Default S3 domain or your custom domain
    file_overwrite = True  # Allow file overwrite (optional)


class DocWallet(models.Model):
    context = models.OneToOneField(Context, on_delete=models.CASCADE, related_name='wallet')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wallet for {self.context}"


class Folder(models.Model):
    name = models.CharField(max_length=255)
    wallet = models.ForeignKey(DocWallet, on_delete=models.CASCADE, related_name='folders')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def folder_path(instance, filename):
    # Get context id and context name (personal/business)
    context_id = instance.folder.wallet.context.id
    context_name = instance.folder.wallet.context.name
    context_name = context_name.replace(' ', '_')

    # Build folder hierarchy (e.g., PermanentWorkingPapers/subfolder1/subfolder2)
    folder_hierarchy = []
    folder = instance.folder
    while folder:
        folder_hierarchy.insert(0, folder.name.replace(' ', '_'))
        folder = folder.parent

    # Join all parts to form the path: context_id/context_name/folder1/folder2/filename
    path = os.path.join(str(context_id), context_name, *folder_hierarchy, filename)
    return path


class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=folder_path, null=True, blank=True, storage=PrivateS3Storage())
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GinIndex(fields=['name'], name='document_name_trgm_idx', opclasses=['gin_trgm_ops']),
        ]

    def save(self, *args, **kwargs):
        # Automatically assign the filename from the uploaded file if 'name' is not provided
        if not self.name:
            self.name = os.path.basename(self.file.name)  # Take the filename from the file path
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


@receiver(post_save, sender=DocWallet)
def create_root_folders(sender, instance, created, **kwargs):
    if created:
        root_folder_names = [
            'PermanentWorkingPapers',
            'CurrentWorkingPapers',
            'OtherDocuments'
        ]
        for folder_name in root_folder_names:
            Folder.objects.create(
                name=folder_name,
                wallet=instance,
                parent=None  # Root folders have no parent
            )


@receiver(pre_save, sender=Document)
def update_file_name_in_s3(sender, instance, **kwargs):
    if not instance.pk:
        return  # New file, nothing to rename

    try:
        old_instance = Document.objects.get(pk=instance.pk)
    except Document.DoesNotExist:
        return  # No old file

    # If the name has changed, but not the folder or file content
    old_name_root, old_ext = os.path.splitext(old_instance.name)
    new_name_root, _ = os.path.splitext(instance.name)

    if old_name_root != new_name_root:
        # Build new file path (preserving original extension)
        new_filename = new_name_root + old_ext
        new_path = folder_path(instance, new_filename)

        storage = instance.file.storage
        old_path = old_instance.file.name

        if storage.exists(old_path):
            with storage.open(old_path, 'rb') as file_content:
                storage.save(new_path, file_content)
            storage.delete(old_path)
            instance.file.name = new_path  # Update DB path
            instance.name = new_filename


@receiver(post_save, sender=Document)
def update_trie_on_new_document(sender, instance, created, **kwargs):
    if created:
        context_id = instance.folder.wallet.context_id
        context_tries[context_id].insert(instance.name)



