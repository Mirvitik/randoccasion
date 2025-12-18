__all__ = ()

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import FormView
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

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


class ActivateUserView(RedirectView):
    pattern_name = "users:login"

    def get_redirect_url(self, *args, **kwargs):
        token = self.kwargs.get("token")
        try:
            activation_token = ActivationToken.objects.get(token=token)

            if not activation_token.is_valid():
                messages.error(self.request, "Срок действия ссылки истек")
                return super().get_redirect_url(*args, **kwargs)

            user = activation_token.user
            user.is_active = True
            user.save()

            activation_token.delete()

            messages.success(self.request, "Аккаунт успешно активирован!")

        except ActivationToken.DoesNotExist:
            messages.error(self.request, "Неверная ссылка активации")

        return reverse(self.pattern_name)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "user_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.filter(
            is_active=True,
        ).select_related("profile")

        query = self.request.GET.get("q")
        maybe_familiar = self.request.GET.get("maybe_familiar")
        sort_by_alpha = self.request.GET.get("sort_alpha")

        if query:
            queryset = q_search(query)

        if maybe_familiar:
            queryset = self.request.user.friends_of_friends

        if sort_by_alpha == "desc":
            return queryset.order_by(
                "-first_name",
                "-last_name",
                "-username",
            )

        return queryset.order_by("first_name", "last_name", "username")


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


class ReactivateAccountView(RedirectView):
    pattern_name = "users:login"

    def get(self, request, *args, **kwargs):
        signed_username = self.kwargs.get("signed_username")

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

        return super().get(request, *args, **kwargs)


class SendFriendRequestView(LoginRequiredMixin, RedirectView):
    pattern_name = "users:user_detail"
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        to_user = get_object_or_404(User, id=user_id)

        if to_user == self.request.user:
            messages.error(self.request, "Вы не можете добавить самого себя.")
            return reverse(self.pattern_name, kwargs={"pk": user_id})

        fr, created = Friendship.objects.get_or_create(
            from_user=self.request.user,
            to_user=to_user,
            defaults={"status": "pending"},
        )

        if not created:
            messages.info(self.request, "Заявка уже отправлена.")
        else:
            message = (
                f"Вам пришла новая заявка в друзья "
                f"от {self.request.user.username}!\n"
                f"Зайдите на сайт и проверьте её"
            )

            if to_user.profile.telegram_id is not None:
                if self.request.user.profile.tg_last_message_date is not None:
                    deltatime = (
                            datetime.datetime.now()
                            - self.request.user.profile.tg_last_message_date
                    )
                    if (deltatime.total_seconds() / 3600) >= 24:
                        self.request.user.profile.tg_messages_cnt = 0
                        self.request.user.profile.tg_last_message_date = None

                if self.request.user.profile.tg_messages_cnt < 10:
                    send_tg_message_sync(
                        tg_id=to_user.profile.telegram_id,
                        message=message,
                    )
                    self.request.user.profile.tg_messages_cnt += 1
                    self.request.user.profile.tg_last_message_date = (
                        datetime.datetime.now()
                    )

            self.request.user.profile.save()
            messages.success(self.request, "Заявка в друзья отправлена.")

        return reverse(self.pattern_name, kwargs={"pk": user_id})


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
