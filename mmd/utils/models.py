from django.db import models

# Create your models here.


class SavedSearch(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_saved_search')
    id_user = models.ForeignKey('user.MyUser', on_delete=models.CASCADE, db_column='id_user')
    query = models.TextField()
    search_date = models.DateField(auto_now_add=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.query

    class Meta:
        db_table = 'saved_searches'
        verbose_name = "SavedSearch"
        verbose_name_plural = "SavedSearches"


class Notification(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_notification')
    id_user = models.ForeignKey('user.MyUser', on_delete=models.CASCADE, db_column='id_user')
    message = models.TextField()
    notification_date = models.DateField(auto_now_add=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = 'notifications'
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"


class ActionLog(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_action_log')
    id_user = models.ForeignKey('user.MyUser', on_delete=models.CASCADE, db_column='id_user')
    action_type = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField()
    old_value = models.TextField()
    new_value = models.TextField()
    ip_address = models.CharField(max_length=50)
    user_agent = models.TextField()
    action = models.TextField()
    action_timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.action

    class Meta:
        db_table = 'action_logs'
        verbose_name = "ActionLog"
        verbose_name_plural = "ActionLogs"
