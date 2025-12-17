__all__ = ()

from django.forms import CharField, DateTimeField, Form
from django.utils.translation import gettext_lazy as _


class APICreateForm(Form):
    name = CharField(
        label=_("Имя ключа"),
        help_text=_("Придумайте имя для ключа"),
    )
    expiry_date = DateTimeField(
        label=_("Дата окончания действия"),
        help_text=_("Введите дату прекращения действия ключа"),
    )
