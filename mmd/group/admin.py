from django.contrib import admin
from group.models import Group,GroupUser

# Register your models here.

admin.site.register(Group)
admin.site.register(GroupUser)