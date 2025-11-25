__all__ = ()

from django.utils.deprecation import MiddlewareMixin

from users.models import User


class UserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user = User.objects.get(pk=request.user.pk)
