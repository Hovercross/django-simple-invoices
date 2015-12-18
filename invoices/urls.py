from django.conf.urls import include, url

urlpatterns = [
    url(r'^invoice/(?P<id>[0-9]+)/$', 'invoices.views.invoice')
]
