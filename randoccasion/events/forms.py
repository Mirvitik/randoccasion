__all__ = ()

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from events.models import Event


class EventCreateForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Event
        fields = [
            "name",
            "image",
            "topic",
            "who_can_see",
            "description",
            "max_participants",
            "location",
            "expires_at",
            "interests",
            "latitude",
            "longitude",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Пикник",
                    "maxlength": "200",
                },
            ),
            "topic": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Отдых на природе",
                },
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                },
            ),
            "who_can_see": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "max_participants": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                },
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Где-то...",
                },
            ),
            "expires_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "interests": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "name": _("Название события"),
            "image": _("Картинка"),
            "topic": _("Тема"),
            "who_can_see": _("Кто может видеть"),
            "description": _("Описание"),
            "max_participants": _("Максимум участников"),
            "location": _("Местоположение"),
            "expires_at": _("Истекает"),
        }
        help_texts = {
            "expires_at": _("Время для записи участников. Минимум 15 минут"),
            "max_participants": _("Минимум 1 участник"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        min_datetime = timezone.now() + timezone.timedelta(hours=3)
        self.fields["expires_at"].widget.attrs["min"] = min_datetime.strftime(
            "%Y-%m-%dT%H:%M",
        )

    def clean_expires_at(self):
        expires_at = self.cleaned_data.get("expires_at")
        if expires_at:
            min_time = timezone.now() + timezone.timedelta(minutes=15)
            if expires_at < min_time:
                raise ValidationError(
                    _("Событие должно истекать не ранее чем через 15 минут"),
                )

        return expires_at

    def clean_max_participants(self):
        max_participants = self.cleaned_data.get("max_participants")
        if max_participants and max_participants < 1:
            raise ValidationError(_("Должен быть хотя бы один участник"))

        return max_participants
