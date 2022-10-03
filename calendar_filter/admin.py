from django.contrib import admin

from . import models


@admin.register(models.RemoteCalendar)
class RemoteCalendarAdmin(admin.ModelAdmin):
    """Basic remote calendar admin"""

    fields = ["name", "url"]


class SubjectExclusionInline(admin.StackedInline):
    model = models.SubjectExclusion
    extra = 0


@admin.register(models.CalendarView)
class CalendarViewAdmin(admin.ModelAdmin):
    """Remote calendar view admin"""

    inlines = [SubjectExclusionInline]
    fields = ["name", "calendar", "calendar_url"]
    readonly_fields = ["calendar_url"]

    def calendar_url(self, o: models.CalendarView) -> str:
        return o.get_absolute_url()
