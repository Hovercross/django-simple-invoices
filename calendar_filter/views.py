"""Views for calendar filter"""

from uuid import UUID

import requests

from icalendar import Calendar
from icalendar.cal import Event

from django.shortcuts import get_object_or_404, render
from django.http.request import HttpRequest
from django.http.response import HttpResponseNotFound, HttpResponse
from django.urls import reverse

from . import models


def calendar_info(request: HttpRequest, key: UUID) -> HttpResponse:
    cal = get_object_or_404(models.CalendarView, key=key)

    cal_url = reverse("calendar_filter:calendar", kwargs={"key": cal.key})
    cal_uri = request.build_absolute_uri(cal_url)

    return render(
        request,
        "calendar_filter/calendar.html",
        context={
            "calendar": cal,
            "cal_url": cal_url,
            "cal_uri": cal_uri,
        },
    )


def calendar_view(request: HttpRequest, key: UUID) -> HttpResponse:
    try:
        cal = (
            models.CalendarView.objects.select_related("calendar")
            .prefetch_related("subject_exclusions")
            .get(key=key)
        )
    except models.CalendarView.DoesNotExist:
        return HttpResponseNotFound()

    cal_download = requests.get(cal.calendar.url)
    if cal_download.status_code != 200:
        resp = HttpResponse(content=cal_download.content)
        resp.status_code = cal_download.status_code
        resp.headers["content-type"] = cal_download.headers["content-type"]
        resp.headers["reason"] = cal_download.reason
        return resp

    ics: Calendar = Calendar.from_ical(cal_download.content)

    def should_include(item) -> bool:
        if not isinstance(item, Event):
            return True

        subject = str(item.get("SUMMARY", ""))
        if not subject:
            return True

        for exclusion in cal.subject_exclusions.all():
            assert isinstance(exclusion, models.SubjectExclusion)

            if subject == exclusion.subject:
                return False

            if not exclusion.case_sensitive:
                if subject.lower() == exclusion.subject.lower():
                    return False

        return True

    new_subcomponents = [item for item in ics.subcomponents if should_include(item)]
    ics.subcomponents = new_subcomponents

    resp = HttpResponse(content=ics.to_ical())
    resp.headers["content-type"] = "text/calendar"

    return resp
