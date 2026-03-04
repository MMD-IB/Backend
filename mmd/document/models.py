from django.db import models

from user.models import MyUser

# Create your models here.

class Document(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_document')
    id_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='id_user')
    title = models.CharField(max_length=30)
    status = models.CharField(max_length=10)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'documents'
        verbose_name = "Document"
        verbose_name_plural = "Documents"


