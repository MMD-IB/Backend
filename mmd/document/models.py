from django.db import models

from user.models import MyUser

# Create your models here.

class Document(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_document')
    id_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='id_user', related_name='documents')
    title = models.CharField(max_length=30)
    content = models.TextField(default="")
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    file_name = models.CharField(max_length=30, default="")
    file_type = models.CharField(max_length=10, default="")
    file_size = models.CharField(max_length=10, default="")
    updated_at = models.DateField(auto_now=True, null=True, blank=True)
    version = models.CharField(max_length=10, default="1.0")
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateField(null=True, blank=True)
    deleted_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='deleted_by', null=True, blank=True, related_name='deleted_documents')
    status = models.CharField(max_length=10)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'documents'
        verbose_name = "Document"
        verbose_name_plural = "Documents"



class ShareDocument(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_share_document')
    id_document = models.ForeignKey(Document, on_delete=models.CASCADE, db_column='id_document')
    id_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='id_user', related_name='shared_documents_received')
    shared_at = models.DateField(auto_now_add=True)
    shared_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='shared_by', related_name='shared_documents_sent')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id_document.title
    
    class Meta:
        db_table = 'share_documents'
        verbose_name = "Share Document"
        verbose_name_plural = "Share Documents"