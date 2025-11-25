__all__ = ()

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from users.forms import ProfileUpdateForm, SignUpForm
from users.models import Profile, User


def signup_view(request):
    template_name = "users/signup.html"
    form = SignUpForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        user = form.save(commit=False)
        user.is_active = settings.DEFAULT_USER_IS_ACTIVE
        user.save()

        Profile.objects.create(user=user)
        if not settings.DEFAULT_USER_IS_ACTIVE:
            activate_link = request.build_absolute_uri(
                reverse("users:activate", kwargs={"username": user.username}),
            )
            send_mail(
                subject="Активация профиля",
                message=f"Для активации перейдите по ссылке: {activate_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.warning(request, "Проверьте почту для активации")
        else:
            messages.success(request, "Регистрация успешна")

        return redirect("users:login")

    context = {"form": form}
    return render(request, template_name, context)


def activate_user_view(request, username):
    try:
        user = User.objects.get(username=username)
        time_limit = user.date_joined + timedelta(hours=12)
        if timezone.now() <= time_limit:
            user.is_active = True
            user.save()
            messages.success(request, "Аккаунт активирован!")
        else:
            messages.error(request, "Ссылка активации просрочена")
    except User.DoesNotExist:
        messages.error(request, "Пользователь не найден")

    return redirect("users:login")


@login_required
def user_list_view(request):
    users_list = User.objects.filter(is_active=True).select_related("profile")
    return render(request, "users/user_list.html", {"user_list": users_list})


def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk, is_active=True)
    return render(request, "users/user_detail.html", {"user": user})


@login_required
def profile_view(request):
    if request.method == "POST":
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
        )
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "PROFILE: Профиль обновлен")
            return redirect("users:profile")
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        "users/profile.html",
        {"profile_form": profile_form},
    )


def reactivate_account(request, signed_username):
    try:
        signer = signing.TimestampSigner()
        username = signer.unsign(signed_username, max_age=3600 * 24 * 7)
        user = User.objects.get(username=username)

        user.is_active = True
        user.attempts_count = 0
        user.save()

        messages.success(request, "Ваш аккаунт успешно активирован!")

    except signing.SignatureExpired:
        messages.error(request, "Ссылка для активации устарела.")

    except (signing.BadSignature, User.DoesNotExist):
        messages.error(request, "Неверная ссылка для активации.")

    return redirect("users:login")
