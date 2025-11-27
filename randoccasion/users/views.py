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
from users.models import Friendship, Profile, User


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


@login_required
def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk, is_active=True)
    are_friends = (
        request.user.is_friends_with(user)
        if request.user.is_authenticated
        else False
    )
    sent_request = (
        request.user.has_sent_request_to(user)
        if request.user.is_authenticated
        else False
    )
    received_request_obj = None
    if (
        request.user.is_authenticated
        and request.user.has_received_request_from(user)
    ):
        received_request_obj = Friendship.objects.get(
            from_user=user,
            to_user=request.user,
            status="pending",
        )

    context = {
        "user": user,
        "are_friends": are_friends,
        "sent_request": sent_request,
        "received_request": received_request_obj,
    }
    return render(request, "users/user_detail.html", context)


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


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        messages.error(request, "Вы не можете добавить самого себя.")
        return redirect("users:user_detail", pk=user_id)

    fr, created = Friendship.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={"status": "pending"},
    )

    if not created:
        messages.info(request, "Заявка уже отправлена.")
    else:
        messages.success(request, "Заявка в друзья отправлена.")

    return redirect("users:user_detail", pk=user_id)


@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(
        Friendship,
        id=request_id,
        to_user=request.user,
        status="pending",
    )
    fr.status = "accepted"
    fr.save()

    messages.success(request, "Заявка принята!")
    return redirect("users:friend_requests")


@login_required
def reject_friend_request(request, request_id):
    fr = get_object_or_404(
        Friendship,
        id=request_id,
        to_user=request.user,
        status="pending",
    )
    fr.status = "rejected"
    fr.save()

    messages.info(request, "Заявка отклонена.")
    return redirect("users:friend_requests")


@login_required
def friends_list_view(request):
    friends = request.user.friends
    return render(request, "users/friends_list.html", {"friends": friends})


@login_required
def friend_requests_view(request):
    friend_requests = Friendship.objects.filter(
        to_user=request.user,
        status="pending",
    )
    return render(
        request,
        "users/friend_requests.html",
        {"friend_requests": friend_requests},
    )
