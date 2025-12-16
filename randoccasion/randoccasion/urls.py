from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = (
    [
        path("i18n/", include("django.conf.urls.i18n")),
    ]
    + i18n_patterns(
        path("admin/", admin.site.urls),
        path("api/v1/", include("api.urls")),
        path("auth/", include("users.urls", namespace="users")),
        path("auth/", include("django.contrib.auth.urls")),
        path("", include("homepage.urls")),
        path("events/", include("events.urls")),
        path("ckeditor5/", include("django_ckeditor_5.urls")),
    )
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
