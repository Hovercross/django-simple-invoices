from django.urls import path

from . import views

app_name = "calendar_filter"
urlpatterns = [
    path("calendar/<uuid:key>.ics", views.calendar_view, name="calendar"),
    path("calendar/<uuid:key>/", views.calendar_info, name="calendar-info"),
]
