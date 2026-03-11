from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("files/", views.file_manager_view, name="file_manager"),
    path("upload/", views.upload_center_view, name="upload_center"),
    path("search/", views.semantic_search_view, name="semantic_search"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/dropdown/", views.notification_dropdown, name="notification_dropdown"),
    path("document/<int:document_id>/preview/", views.document_preview, name="document_preview"),
    path("logout/", views.logout, name="logout"),
]
