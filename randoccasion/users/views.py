__all__ = ()

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import FormView
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from users.forms import ProfileUpdateForm, SignUpForm
from users.models import ActivationToken, Friendship, Profile, User
from users.utils import q_search
from users.utils import send_tg_message_sync


class SignUpView(FormView):
    template_name = "users/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = settings.DEFAULT_USER_IS_ACTIVE
        user.save()

        Profile.objects.create(user=user)

        if not settings.DEFAULT_USER_IS_ACTIVE:
            self._send_activation_email(user)
            messages.warning(
                self.request,
                "Проверьте почту для активации аккаунта",
            )
        else:
            messages.success(
                self.request,
                f"Добро пожаловать, {user.username}!",
            )

        return super().form_valid(form)

    def _send_activation_email(self, user):
        activation_token = ActivationToken.create_for_user(user)

        activate_link = self.request.build_absolute_uri(
            reverse(
                "users:activate",
                kwargs={"token": activation_token.token},
            ),
        )

        send_mail(
            subject="Активация профиля на сайте",
            message=f"""
            Здравствуйте, {user.username}!

            Для активации вашего аккаунта перейдите по ссылке:
            {activate_link}

            Ссылка действительна 24 часа.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    def form_invalid(self, form):
        messages.error(self.request, "Исправьте ошибки в форме регистрации")
        return super().form_invalid(form)


def activate_user_view(request, token):
    try:
        activation_token = ActivationToken.objects.get(
            token=token,
            is_used=False,
        )
        if not activation_token.is_valid():
            messages.error(request, "Срок действия ссылки истек")
            return redirect("login")

        user = activation_token.user
        user.is_active = True
        user.save()

        activation_token.is_used = True
        activation_token.save()

        messages.success(request, "Аккаунт успешно активирован!")
        return redirect("login")

    except ActivationToken.DoesNotExist:
        messages.error(request, "Неверная ссылка активации")
        return redirect("login")


@login_required
def user_list_view(request):
    query = request.GET.get("q")
    maybe_familiar = request.GET.get("maybe_familiar")
    sort_by_alpha = request.GET.get("sort_alpha")
    if query:
        users_list = q_search(query)
    else:
        users_list = User.objects.filter(
            is_active=True,
        ).select_related("profile")

    if maybe_familiar:
        users_list = request.user.friends_of_friends

    if sort_by_alpha == "desc":
        users_list = users_list.order_by(
            "-first_name",
            "-last_name",
            "-username",
        )
    elif sort_by_alpha == "asc":
        users_list = users_list.order_by("first_name", "last_name", "username")

    return render(request, "users/user_list.html", {"user_list": users_list})


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        return get_object_or_404(self.get_queryset(), pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        request_user = self.request.user

        are_friends = (
            request_user.is_friends_with(user)
            if request_user.is_authenticated
            else False
        )

        sent_request = (
            request_user.has_sent_request_to(user)
            if request_user.is_authenticated
            else False
        )

        received_request_obj = None
        if (
            request_user.is_authenticated
            and request_user.has_received_request_from(user)
        ):
            received_request_obj = Friendship.objects.get(
                from_user=user,
                to_user=request_user,
                status="pending",
            )

        context.update(
            {
                "are_friends": are_friends,
                "sent_request": sent_request,
                "received_request": received_request_obj,
            },
        )

        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "PROFILE: Профиль обновлен")
        return redirect(self.success_url)

    def form_invalid(self, form):
        first_error = list(form.errors.values())[0][0]
        messages.warning(self.request, f"PROFILE: Ошибка - {first_error}")
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        return self.request.user.profile


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
        message = (
            f"Вам пришла новая заявка в друзья от {request.user.username}!\n"
            f"Зайдите на сайт и проверьте её"
        )
        if to_user.profile.telegram_id is not None:
            if request.user.profile.tg_last_message_date is not None:
                deltatime = (
                    datetime.datetime.now()
                    - request.user.profile.tg_last_message_date
                )
                if (deltatime.total_seconds() / 3600) >= 24:
                    request.user.profile.tg_messages_cnt = 0
                    request.user.profile.tg_last_message_date = None

            if request.user.profile.tg_messages_cnt < 10:
                send_tg_message_sync(
                    tg_id=to_user.profile.telegram_id,
                    message=message,
                )
                request.user.profile.tg_messages_cnt += 1
                request.user.profile.tg_last_message_date = (
                    datetime.datetime.now()
                )

        request.user.profile.save()
        messages.success(request, "Заявка в друзья отправлена.")

    return redirect("users:user_detail", pk=user_id)


class AcceptFriendRequest(LoginRequiredMixin, RedirectView):
    pattern_name = "users:friend_requests"
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        request_id = kwargs.get("request_id")
        fr = get_object_or_404(
            Friendship,
            id=request_id,
            to_user=self.request.user,
            status="pending",
        )
        fr.status = "accepted"
        fr.save()

        messages.success(self.request, "Заявка принята!")
        return reverse(self.pattern_name)


class RejectFriendRequest(LoginRequiredMixin, RedirectView):
    pattern_name = "users:friend_requests"
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        request_id = kwargs.get("request_id")
        fr = get_object_or_404(
            Friendship,
            id=request_id,
            to_user=self.request.user,
            status="pending",
        )
        fr.status = "rejected"
        fr.save()

        messages.info(self.request, "Заявка отклонена.")
        return reverse(self.pattern_name)


class FriendsListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/friends_list.html"
    context_object_name = "friends"

    def get_queryset(self):
        return self.request.user.friends.order_by("username")


class FriendRequestsView(LoginRequiredMixin, ListView):
    model = Friendship
    template_name = "users/friend_requests.html"
    context_object_name = "friend_requests"

    def get_queryset(self):
        return Friendship.objects.filter(
            to_user=self.request.user,
            status="pending",
        )


class RemoveFriendView(LoginRequiredMixin, RedirectView):
    pattern_name = "users:friends_list"
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        friend_id = kwargs.get("friend_id")
        friend = get_object_or_404(User, id=friend_id)

        Friendship.objects.filter(
            Q(from_user=self.request.user, to_user=friend, status="accepted")
            | Q(
                from_user=friend,
                to_user=self.request.user,
                status="accepted",
            ),
        ).delete()

        messages.success(
            self.request,
            f"Вы удалили {friend.username} из друзей",
        )
        return reverse_lazy(self.pattern_name)
