from django.contrib import admin
from django.urls import path, include
from app.api import api  # Import the NinjaExtraAPI instance

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),  # Include the Django Ninja Extra API URLs
]
