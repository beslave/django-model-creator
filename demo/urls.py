from django.conf.urls import patterns, include, url
from django.contrib import admin

import model_creator.urls


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^model_creator/',
        include(model_creator.urls, namespace='model_creator')
    ),
)
