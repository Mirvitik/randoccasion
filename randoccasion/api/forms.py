__all__ = ()

from django.forms import CharField, DateTimeField, Form


class APICreateForm(Form):
    name = CharField(label="Имя ключа", help_text="Придумайте имя для ключа")
    expiry_date = DateTimeField(
        label="Дата окончания действия",
        help_text="Введите дату прекращения действия ключа",
    )
