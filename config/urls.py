from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "CV admin"
admin.site.site_title = "CV admin"
admin.site.index_title = "Manage your CV"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("portfolio.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
