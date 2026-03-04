from django.db import models

# Create your models here.

class MyUser(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_user')
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')  # Mappa alla colonna esistente
    role = models.CharField(max_length=10, default="user")
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"
    
    class Meta:
        db_table = 'users'  # Mappa alla tabella esistente
        verbose_name = "MyUser"
        verbose_name_plural = "MyUsers"


