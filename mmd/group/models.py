from django.db import models
from user.models import MyUser


# Create your models here.

class Group(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_group')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'groups'
        verbose_name = "Group"
        verbose_name_plural = "Groups"
    
class GroupUser(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_group_user')
    id_group = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='id_group')
    id_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='id_user')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_group.name} - {self.id_user.name}"

    class Meta:
        db_table = 'group_users'
        verbose_name = "GroupUser"
        verbose_name_plural = "GroupUsers"
