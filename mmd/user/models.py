from django.db import models

# Create your models here.

class MyUser(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_user')
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')  # Mappa alla colonna esistente

    def __str__(self):
        return f"{self.name} {self.surname}"
    
    class Meta:
        db_table = 'users'  # Mappa alla tabella esistente
        verbose_name = "MyUser"
        verbose_name_plural = "MyUsers"


