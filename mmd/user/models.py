from django.db import models

# Create your models here.

class MyUser(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=20)

    def __str__(self):
        return super().__str__()
    
    class Meta:
        verbose_name = "MyUser"
        verbose_name_plural = "MyUsers"


