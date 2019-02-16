# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Define urls used in this application."""

from django.conf.urls import include, url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

urlpatterns = [
    url(r'', include('rest_api.urls', namespace='rest_framework')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

# Change admin site title
admin.site.site_header = _("MySunBuddyinc Administration")
admin.site.site_title = _("MySunBuddyinc Admin")