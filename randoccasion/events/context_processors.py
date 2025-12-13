__all__ = ()

from django.conf import settings


def get_ymaps_token(request):
    return {
        "ymaps_api": settings.YMAPS_API,
    }
