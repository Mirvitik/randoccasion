__all__ = ()

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.forms import UserChangeForm
from users.models import Interest, Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    fields = (
        Profile.birthday.field.name,
        Profile.image.field.name,
        Profile.interests.field.name,
    )
    filter_horizontal = (Profile.interests.field.name,)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    inlines = (ProfileInline,)
    readonly_fields = (
        User.last_login.field.name,
        User.date_joined.field.name,
    )


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)
admin.site.register(Profile)


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")
