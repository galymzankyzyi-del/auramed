from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('doctors/', include('doctors.urls')),

    path(
        "google78f6840d871893f4.html",
        lambda request: HttpResponse(
            "google-site-verification: google4d159c0f25916483.html",
            content_type="text/plain",
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )