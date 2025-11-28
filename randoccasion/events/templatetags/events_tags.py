__all__ = ()

from django.template import Library
from django.utils.http import urlencode

register = Library()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context["request"].GET.dict()
    query.update(kwargs)

    return urlencode(query)
