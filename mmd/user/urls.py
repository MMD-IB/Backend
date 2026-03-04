from django.urls import path
from .views import user_index

urlpatterns = [
    path("dashboard/", user_index, name="dashboard"),
]
