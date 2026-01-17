from django.db import models

from user.models import MyUser

# Create your models here.

class Document(models.Model):
    id_user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    status = models.CharField(max_length=10)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return super().__str__()
    
    def get_document_by_id(id):
        pass

    def get_all_document():
        pass

    def post_document(id_user, title, status):
        pass

    def delete_document(id):
        pass

    def patch_document(id, id_user, title, status):
        pass

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"


