__all__ = ()

from django.contrib import admin

from events.models import Event, EventRequest


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(EventRequest)
