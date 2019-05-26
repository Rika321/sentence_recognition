from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('text_classifier/', include('text_classifier.urls')),
    path('admin/', admin.site.urls),
]
