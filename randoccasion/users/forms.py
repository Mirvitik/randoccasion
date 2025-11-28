__all__ = ()

from datetime import date

from django import forms
from django.contrib import auth
from django.core.validators import MinValueValidator

from users.models import Interest, Profile, User


class UserChangeForm(auth.forms.UserChangeForm):
    password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta(auth.forms.UserChangeForm.Meta):
        fields = [
            User.first_name.field.name,
            User.last_name.field.name,
            User.email.field.name,
        ]
        exclude = [
            User.password.field.name,
        ]
        model = User


class SignUpForm(auth.forms.UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta(auth.forms.UserCreationForm.Meta):
        fields = [
            User.username.field.name,
            "email",
            "password1",
            "password2",
        ]
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()

        return user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует",
            )

        return email


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    telegram_id = forms.IntegerField(
        label="Telegram ID",
        validators=[MinValueValidator(1)],
    )
    first_name = forms.CharField(label="Имя", required=False, max_length=40)
    last_name = forms.CharField(label="Фамилия", required=False, max_length=40)
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Интересы",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.user:
            self.initial["telegram_id"] = self.instance.telegram_id
            self.initial["email"] = self.instance.user.email
            self.initial["first_name"] = self.instance.user.first_name
            self.initial["last_name"] = self.instance.user.last_name

        if self.instance.birthday:
            self.initial["birthday"] = self.instance.birthday.strftime(
                "%Y-%m-%d",
            )

        for field in self.visible_fields():
            if not isinstance(
                field.field.widget,
                forms.CheckboxSelectMultiple,
            ):
                field.field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        user.profile.telegram_id = self.cleaned_data["telegram_id"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            profile.save()
            self.save_m2m()

        return profile

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if (
                User.objects.filter(email=email)
                .exclude(id=self.instance.user.id)
                .exists()
            ):
                raise forms.ValidationError(
                    "Этот email уже используется другим пользователем",
                )

        return email

    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")
        if birthday:
            today = date.today()
            earliest = today.replace(year=today.year - 150)
            latest = today

            if birthday < earliest:
                raise forms.ValidationError(
                    "Дата рождения не может быть старше 150 лет.",
                )

            if birthday > latest:
                raise forms.ValidationError("Дата не может быть в будущем.")

        return birthday

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image

        max_size = 2 * 1024 * 1024
        if image.size > max_size:
            raise forms.ValidationError("Размер не должен превышать 2 МБ")

        return image

    class Meta:
        model = Profile
        fields = [
            "birthday",
            "image",
            "interests",
        ]
        widgets = {
            "birthday": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
            ),
            Profile.interests.field.name: forms.CheckboxSelectMultiple(),
        }
