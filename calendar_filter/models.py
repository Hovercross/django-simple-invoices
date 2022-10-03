from django.db import models
from django.urls import reverse

from uuid import uuid4


class RemoteCalendar(models.Model):
    name = models.CharField(max_length=256, unique=True)
    url = models.URLField(verbose_name="URL")

    def __str__(self):
        return self.name


class CalendarView(models.Model):
    name = models.CharField(max_length=256, unique=True)
    calendar = models.ForeignKey(RemoteCalendar, on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid4)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse("calendar_filter:calendar")
        return reverse("calendar_filter:calendar-info", kwargs={"key": self.key})


class SubjectExclusion(models.Model):
    view = models.ForeignKey(
        CalendarView, on_delete=models.CASCADE, related_name="subject_exclusions"
    )
    subject = models.CharField(max_length=4096)
    case_sensitive = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
